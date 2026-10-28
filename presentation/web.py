from decimal import Decimal
import logging
from fastapi import Request, Form, UploadFile, File, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, ConfigDict
from starlette.exceptions import HTTPException
from domain.search.image_query import ImageQuery
from domain.search.voice_query import VoiceQuery


class QuantityInput(BaseModel):
    model_config = ConfigDict(strict=True)
    quantity: int = Field(gt=0, le=999)


def configure_routes(app, template_root):
    templates = Jinja2Templates(directory=template_root)
    templates.env.filters["money"] = lambda amount: f"{amount:,.0f} ₫"

    def render(request, name, **context):
        return templates.TemplateResponse(request=request, name=name, context=context)

    def scope(request):
        return request.app.state.container.scope()

    @app.exception_handler(HTTPException)
    async def http_error(request, error):
        return templates.TemplateResponse(request=request, name="error.html",
            context={"message": "Page not found" if error.status_code == 404 else str(error.detail)},
            status_code=error.status_code)

    @app.exception_handler(Exception)
    async def unexpected_error(request, error):
        logging.getLogger(__name__).error("Request failed", exc_info=error)
        return templates.TemplateResponse(request=request, name="error.html",
            context={"message": "We could not complete your request. Please try again."}, status_code=500)

    @app.exception_handler(ValueError)
    async def invalid(request, error):
        if request.headers.get("accept") == "application/json":
            return JSONResponse({"detail": str(error)}, status_code=400)
        return templates.TemplateResponse(request=request, name="error.html",
            context={"message": str(error)}, status_code=400)

    @app.exception_handler(LookupError)
    async def missing(request, error):
        return templates.TemplateResponse(request=request, name="error.html",
            context={"message": str(error)}, status_code=404)

    @app.exception_handler(RequestValidationError)
    async def validation(request, error):
        if request.headers.get("accept") == "application/json":
            return JSONResponse({"detail": "Please check the submitted values."}, status_code=422)
        return templates.TemplateResponse(request=request, name="error.html",
            context={"message": "Please check the submitted values and try again."}, status_code=422)

    @app.get("/")
    def home(request: Request):
        with scope(request) as services:
            products = services.search._catalog()
            category_products = []
            seen_categories = set()
            for product in products:
                category = product.category.categoryName
                if category not in seen_categories:
                    category_products.append(product)
                    seen_categories.add(category)
            return render(request, "home.html", products=products[:8], deals=products[8:12],
                categories=sorted({product.category.categoryName for product in products}),
                category_products=category_products,
                recommendations=services.recommendation.getRecommendations(1, 1))

    @app.get("/search")
    def search(request: Request, q: str = "", category: str = "", brand: str = "",
               minimum: Decimal = Query(0, ge=0), maximum: Decimal | None = Query(None, ge=0),
               available: bool = False, sort: str = "relevance", image: str = "", transcript: str = ""):
        with scope(request) as services:
            if image:
                results = services.search.search(ImageQuery(imageReference=image))
                modality, summary = "Image", "Visual matches"
            elif transcript:
                results = services.search.search(VoiceQuery(transcribedText=transcript))
                modality, summary = "Voice", transcript
            else:
                results = services.search._text(q or "electronics")
                modality, summary = "Text", q
            catalog = services.search._catalog()
            results = services.search._filterResults(results, category, brand, minimum, maximum, available, sort)
            return render(request, "search_results.html", results=results, modality=modality, summary=summary,
                q=q, image=image, transcript=transcript, category=category, brand=brand, minimum=minimum,
                maximum=maximum, available=available, sort=sort,
                categories=sorted({product.category.categoryName for product in catalog}),
                brands=sorted({product.brand for product in catalog}))

    @app.post("/search/image")
    async def image_search(request: Request, image: UploadFile = File(...)):
        content = await image.read(5 * 1024 * 1024 + 1)
        with scope(request) as services:
            reference, results = services.search._image(content, image.filename or "", image.content_type or "")
        return RedirectResponse("/search?image=" + reference, status_code=303)

    @app.post("/search/voice")
    def voice_search(request: Request, transcript: str = Form(...)):
        from urllib.parse import urlencode
        with scope(request) as services:
            services.search._voice(transcript)
        return RedirectResponse("/search?" + urlencode({"transcript": transcript}), status_code=303)

    @app.get("/products/{productId}")
    def product_detail(request: Request, productId: int):
        if productId <= 0:
            raise ValueError("Invalid product ID")
        with scope(request) as services:
            product = services.search._product(productId, 1)
            return render(request, "product_detail.html", product=product,
                recommendations=services.recommendation.getRecommendations(1, productId))

    @app.get("/api/recommendations")
    def recommendations(request: Request, customerId: int = Query(1, gt=0), productId: int = Query(1, gt=0)):
        with scope(request) as services:
            return services.recommendation.getRecommendations(customerId, productId)

    @app.get("/cart")
    def cart_view(request: Request):
        with scope(request) as services:
            cart = services.cart.viewCart(1)
            return render(request, "cart.html", cart=cart,
                recommendations=services.recommendation.getRecommendations(1, cart.items[0].product.productId if cart.items else 1))

    @app.post("/cart/items")
    def add_item(request: Request, productId: int = Form(..., gt=0), quantity: int = Form(1, gt=0, le=999)):
        with scope(request) as services:
            cart = services.cart.addItem(services.cart.viewCart(1).cartId, productId, quantity)
            if request.headers.get("accept") == "application/json":
                return {"message": "Added to cart", "count": sum(item.quantity for item in cart.items)}
        return RedirectResponse("/cart", status_code=303)

    @app.patch("/cart/items/{productId}")
    def update_item(request: Request, productId: int, payload: QuantityInput):
        with scope(request) as services:
            services.cart.updateQuantity(services.cart.viewCart(1).cartId, productId, payload.quantity)
        return {"message": "Cart updated"}

    @app.delete("/cart/items/{productId}")
    def remove_item(request: Request, productId: int):
        with scope(request) as services:
            services.cart.removeItem(services.cart.viewCart(1).cartId, productId)
        return {"message": "Item removed"}

    @app.get("/checkout")
    def checkout_view(request: Request):
        with scope(request) as services:
            cart = services.cart.viewCart(1)
            return render(request, "checkout.html", cart=cart, customer=services.customer)

    @app.post("/checkout")
    def checkout(request: Request, shippingAddress: str = Form(...), recipientPhone: str = Form(...),
                 paymentMethod: str = Form("Cash on Delivery"), simulateFailure: bool = Form(False)):
        with scope(request) as services:
            services.checkout.service.payment_method = paymentMethod
            services.checkout.service.simulate_failure = simulateFailure
            order = services.checkout.checkout(services.cart.viewCart(1).cartId, shippingAddress, recipientPhone)
        return RedirectResponse(f"/orders/{order.orderId}/success", status_code=303)

    @app.get("/orders")
    def order_list(request: Request):
        with scope(request) as services:
            return render(request, "orders.html", orders=services.order._listOrders(1))

    def order_page(request, orderId, template):
        with scope(request) as services:
            order = services.order.viewOrder(orderId)
            return render(request, template, order=order, payment=services.order._getPayment(orderId),
                          shipment=services.order.trackOrder(orderId))

    @app.get("/orders/{orderId}/success")
    def success(request: Request, orderId: int):
        return order_page(request, orderId, "order_success.html")

    @app.get("/orders/{orderId}")
    def order_detail(request: Request, orderId: int):
        return order_page(request, orderId, "order_detail.html")

    @app.get("/orders/{orderId}/tracking")
    def tracking(request: Request, orderId: int):
        return order_page(request, orderId, "order_tracking.html")

