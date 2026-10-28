from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class PaymentStatus(StrEnum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"


@dataclass
class Payment:
    paymentId: int
    paymentMethod: str
    amount: Decimal
    status: PaymentStatus
    transactionCode: str
    paidAt: datetime | None
    _orderId: int = field(default=0, repr=False, compare=False)

