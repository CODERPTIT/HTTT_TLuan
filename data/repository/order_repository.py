from copy import copy
from datetime import datetime
from sqlalchemy import select
from domain.order.order import Order, OrderStatus
from domain.order.order_item import OrderItem
from data.infrastructure.order_database import orders, order_items


class OrderRepository:
    def __init__(self, connection, products):
        self.connection = connection
        self.products = products

    def findById(self, orderId: int) -> Order:
        row = self.connection.execute(select(orders).where(orders.c.id == orderId)).mappings().first()
        if row is None:
            raise LookupError("Order not found")
        items = []
        for item in self.connection.execute(select(order_items).where(order_items.c.order_id == orderId)).mappings():
            product = copy(self.products.findById(item["product_id"]))
            product.price = item["price_snapshot"]
            items.append(OrderItem(item["id"], item["quantity"], product))
        return Order(row["id"], row["address"], row["phone"], row["customer_id"],
                     datetime.fromisoformat(row["date"]), OrderStatus(row["status"]), items)

    def findByCustomer(self, customerId: int) -> list[Order]:
        return [self.findById(identity) for identity in self.connection.execute(
            select(orders.c.id).where(orders.c.customer_id == customerId).order_by(orders.c.id.desc())).scalars()]

    def save(self, order: Order) -> None:
        order.orderId = self.connection.execute(orders.insert().values(customer_id=order.customerId,
            address=order.shippingAddress, phone=order.recipientPhone, date=order.orderDate.isoformat(),
            status=order.status)).inserted_primary_key[0]
        for item in order.items:
            item.orderItemId = self.connection.execute(order_items.insert().values(order_id=order.orderId,
                product_id=item.product.productId, quantity=item.quantity,
                price_snapshot=item.product.price)).inserted_primary_key[0]

    def update(self, order: Order) -> None:
        self.connection.execute(orders.update().where(orders.c.id == order.orderId).values(status=order.status))

