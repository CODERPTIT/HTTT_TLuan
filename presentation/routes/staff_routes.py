from decimal import Decimal

from fastapi import Form, Request
from fastapi.responses import RedirectResponse


def register_staff_routes(app, web):
    @app.get("/staff")
    def staff_dashboard(request: Request):
        with web.scope(request) as services:
            account = web.requireRole(request, services,
                "ADMINISTRATOR", "SALES_STAFF", "WAREHOUSE_STAFF", "MANAGER")
            role = account["role"]
            return web.render(request, "staff.html", role=role,
                products=services.staff.products() if role in {"ADMINISTRATOR", "WAREHOUSE_STAFF"} else [],
                orders=services.staff.orders() if role in {"SALES_STAFF", "WAREHOUSE_STAFF"} else [],
                report=services.staff.report() if role == "MANAGER" else None)

    @app.post("/staff/products/{productId}")
    def staff_product(request: Request, productId: int, price: Decimal = Form(...), status: str = Form(...)):
        with web.scope(request) as services:
            web.requireRole(request, services, "ADMINISTRATOR")
            services.staff.updateProduct(productId, price, status)
        return RedirectResponse("/staff", status_code=303)

    @app.post("/staff/stock/{productId}")
    def staff_stock(request: Request, productId: int, quantity: int = Form(...)):
        with web.scope(request) as services:
            web.requireRole(request, services, "WAREHOUSE_STAFF")
            services.staff.updateStock(productId, quantity)
        return RedirectResponse("/staff", status_code=303)

    @app.post("/staff/orders/{orderId}/process")
    def staff_process(request: Request, orderId: int):
        with web.scope(request) as services:
            web.requireRole(request, services, "SALES_STAFF")
            services.staff.processOrder(orderId)
        return RedirectResponse("/staff", status_code=303)

    @app.post("/staff/orders/{orderId}/ship")
    def staff_ship(request: Request, orderId: int):
        with web.scope(request) as services:
            web.requireRole(request, services, "WAREHOUSE_STAFF")
            services.staff.shipOrder(orderId)
        return RedirectResponse("/staff", status_code=303)
