from fastapi import Request
from fastapi.responses import RedirectResponse


def register_shipping_provider_routes(app, web):
    @app.get("/shipping")
    def shipping_dashboard(request: Request):
        with web.scope(request) as services:
            account = web.requireRole(request, services, "SHIPPING_PROVIDER")
            return web.render(request, "shipping_provider.html",
                shipments=services.shipping_provider.shipments(account["shipping_provider_id"]))

    @app.post("/shipping/orders/{orderId}/out-for-delivery")
    def out_for_delivery(request: Request, orderId: int):
        with web.scope(request) as services:
            account = web.requireRole(request, services, "SHIPPING_PROVIDER")
            services.shipping_provider.markOutForDelivery(account["shipping_provider_id"], orderId)
        return RedirectResponse("/shipping", status_code=303)

    @app.post("/shipping/orders/{orderId}/deliver")
    def delivered(request: Request, orderId: int):
        with web.scope(request) as services:
            account = web.requireRole(request, services, "SHIPPING_PROVIDER")
            services.shipping_provider.markDelivered(account["shipping_provider_id"], orderId)
        return RedirectResponse("/shipping", status_code=303)
