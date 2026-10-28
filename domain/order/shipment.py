from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class ShipmentStatus(StrEnum):
    PREPARING = "PREPARING"
    SHIPPED = "SHIPPED"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"


@dataclass
class Shipment:
    trackingNumber: str
    status: ShipmentStatus
    carrier: str
    estimatedDeliveryDate: datetime
    deliveredAt: datetime | None = None
    _orderId: int = field(default=0, repr=False, compare=False)

