from fastapi import Form, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException


class QuantityInput(BaseModel):
    model_config = ConfigDict(strict=True)
    quantity: int = Field(gt=0, le=999)


def register_commerce_routes(app, web):
    @app.get("/cart")
    def cart_view(request: Request):
        with web.scope(request) as services:
            identity = web.customerId(request, services)
            cart = services.cart.viewCart(identity)
            productId = cart.items[0].product.productId if cart.items else 1
            return web.render(request, "cart.html", cart=cart,
                recommendations=services.recommendation.getRecommendations(identity, productId))

    @app.post("/cart/items")
    def add_item(request: Request, productId: int = Form(..., gt=0), quantity: int = Form(1, gt=0, le=999)):
        with web.scope(request) as services:
            identity = web.customerId(request, services)
            cart = services.cart.addItem(services.cart.viewCart(identity).cartId, productId, quantity)
            if request.headers.get("accept") == "application/json":
                return {"message": "Added to cart", "count": sum(item.quantity for item in cart.items)}
        return RedirectResponse("/cart", status_code=303)

    @app.patch("/cart/items/{productId}")
    def update_item(request: Request, productId: int, payload: QuantityInput):
        with web.scope(request) as services:
            cart = services.cart.viewCart(web.customerId(request, services))
            services.cart.updateQuantity(cart.cartId, productId, payload.quantity)
        return {"message": "Cart updated"}

    @app.delete("/cart/items/{productId}")
    def remove_item(request: Request, productId: int):
        with web.scope(request) as services:
            cart = services.cart.viewCart(web.customerId(request, services))
            services.cart.removeItem(cart.cartId, productId)
        return {"message": "Item removed"}

    @app.get("/checkout")
    def checkout_view(request: Request):
        with web.scope(request) as services:
            identity = web.customerId(request, services)
            return web.render(request, "checkout.html", cart=services.cart.viewCart(identity),
                              customer=services.customers.getCustomer(identity))

    @app.post("/checkout")
    def checkout(request: Request, shippingAddress: str = Form(...), recipientPhone: str = Form(...),
                 paymentMethod: str = Form("Cash on Delivery"), simulateFailure: bool = Form(False)):
        with web.scope(request, immediate=True) as services:
            identity = web.customerId(request, services)
            services.checkout.service.payment_method = paymentMethod
            services.checkout.service.simulate_failure = simulateFailure
            order = services.checkout.checkout(services.cart.viewCart(identity).cartId,
                                               shippingAddress, recipientPhone)
        return RedirectResponse(f"/orders/{order.orderId}/success", status_code=303)

    @app.get("/orders")
    def order_list(request: Request):
        with web.scope(request) as services:
            orders = services.order.listOrders(web.customerId(request, services))
            return web.render(request, "orders.html", orders=orders)

    def order_page(request, orderId, template):
        with web.scope(request) as services:
            identity = web.customerId(request, services)
            order = services.order.viewOrder(orderId)
            if order.customerId != identity:
                raise HTTPException(status_code=404, detail="Order not found")
            return web.render(request, template, order=order, payment=services.order.getPayment(orderId),
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
