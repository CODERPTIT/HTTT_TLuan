import logging
from urllib.parse import quote

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException

from presentation.routes.auth_routes import register_auth_routes
from presentation.routes.catalog_routes import register_catalog_routes
from presentation.routes.commerce_routes import register_commerce_routes
from presentation.routes.staff_routes import register_staff_routes
from presentation.routes.shipping_provider_routes import register_shipping_provider_routes
from presentation.web_context import WebContext


def configure_routes(app, template_root):
    templates = Jinja2Templates(directory=template_root)
    templates.env.filters["money"] = lambda amount: f"{amount:,.0f} ₫"
    web = WebContext(templates)

    @app.exception_handler(HTTPException)
    async def http_error(request, error):
        if error.status_code == 401 and request.headers.get("accept") != "application/json":
            destination = request.url.path
            if request.method not in {"GET", "HEAD"}:
                destination = ("/cart" if destination.startswith("/cart") else
                               "/checkout" if destination.startswith("/checkout") else
                               "/staff" if destination.startswith("/staff") else "/")
                if request.url.path.startswith("/shipping"):
                    destination = "/shipping"
            return RedirectResponse("/login?next=" + quote(destination, safe="/"), status_code=303)
        if request.headers.get("accept") == "application/json":
            return JSONResponse({"detail": str(error.detail)}, status_code=error.status_code)
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

    register_auth_routes(app, web)
    register_catalog_routes(app, web)
    register_commerce_routes(app, web)
    register_staff_routes(app, web)
    register_shipping_provider_routes(app, web)
