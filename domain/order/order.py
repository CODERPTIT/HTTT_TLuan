from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from domain.order.order_item import OrderItem


class OrderStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


@dataclass
class Order:
    orderId: int
    shippingAddress: str
    recipientPhone: str
    customerId: int
    orderDate: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: OrderStatus = OrderStatus.PENDING
    items: list[OrderItem] = field(default_factory=list)

    def updateStatus(self, status: OrderStatus) -> None:
        self.status = OrderStatus(status)

