from decimal import Decimal

from sqlalchemy import func, select

from data.infrastructure.order_database import customers, users, order_items, orders, payments, shipments
from data.infrastructure.product_database import products


class StaffRepository:
    def __init__(self, connection):
        self.connection = connection

    def products(self):
        return self.connection.execute(select(products).order_by(products.c.id)).mappings().all()

    def orders(self):
        return self.connection.execute(select(orders.c.id, orders.c.status, orders.c.date,
            users.c.full_name.label("customer"), shipments.c.status.label("shipment_status"))
            .join(customers, orders.c.customer_id == customers.c.id)
            .join(users, customers.c.id == users.c.id)
            .outerjoin(shipments, shipments.c.order_id == orders.c.id)
            .order_by(orders.c.id.desc())).mappings().all()

    def update_product(self, product_id: int, price: Decimal, status: str):
        if price <= 0 or status not in {"ACTIVE", "DISCONTINUED", "OUT_OF_STOCK"}:
            raise ValueError("Invalid price or product status")
        changed = self.connection.execute(products.update().where(products.c.id == product_id)
            .values(price=price, status=status))
        if not changed.rowcount:
            raise LookupError("Product not found")

    def update_stock(self, product_id: int, quantity: int):
        if quantity < 0 or quantity > 100000:
            raise ValueError("Invalid stock quantity")
        changed = self.connection.execute(products.update().where(products.c.id == product_id)
            .values(quantity_available=quantity))
        if not changed.rowcount:
            raise LookupError("Product not found")

    def process_order(self, order_id: int):
        changed = self.connection.execute(orders.update().where(
            orders.c.id == order_id, orders.c.status == "CONFIRMED").values(status="PROCESSING"))
        if not changed.rowcount:
            raise ValueError("Only confirmed orders can be processed")

    def ship_order(self, order_id: int):
        shipment = self.connection.execute(select(shipments.c.tracking).where(
            shipments.c.order_id == order_id)).first()
        if shipment is None:
            raise ValueError("Shipment not found for this order")
        changed = self.connection.execute(orders.update().where(
            orders.c.id == order_id, orders.c.status == "PROCESSING").values(status="SHIPPED"))
        if not changed.rowcount:
            raise ValueError("Only processing orders can be shipped")
        self.connection.execute(shipments.update().where(shipments.c.order_id == order_id).values(status="SHIPPED"))

    def report(self):
        order_count = self.connection.execute(select(func.count()).select_from(orders)).scalar_one()
        product_count = self.connection.execute(select(func.count()).select_from(products)).scalar_one()
        paid_revenue = self.connection.execute(select(func.coalesce(func.sum(payments.c.amount), 0))
            .where(payments.c.status == "PAID")).scalar_one()
        units_sold = self.connection.execute(select(func.coalesce(func.sum(order_items.c.quantity), 0))
            .select_from(order_items.join(orders, order_items.c.order_id == orders.c.id))
            .where(orders.c.status != "CANCELLED")).scalar_one()
        return {"orders": order_count, "products": product_count,
                "paid_revenue": paid_revenue, "units_sold": units_sold}
