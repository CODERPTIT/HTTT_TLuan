from datetime import datetime
from sqlalchemy import select
from domain.order.payment import Payment, PaymentStatus
from data.infrastructure.order_database import payments


class PaymentRepository:
    def __init__(self, connection):
        self.connection = connection

    def findByOrder(self, orderId: int) -> Payment:
        row = self.connection.execute(select(payments).where(payments.c.order_id == orderId)).mappings().first()
        if row is None:
            raise LookupError("Payment not found")
        return Payment(row["id"], row["method"], row["amount"], PaymentStatus(row["status"]), row["code"],
                       datetime.fromisoformat(row["paid_at"]) if row["paid_at"] else None, row["order_id"])

    def save(self, payment: Payment) -> None:
        if payment._orderId <= 0:
            raise ValueError("Payment must be associated with an order")
        payment.paymentId = self.connection.execute(payments.insert().values(order_id=payment._orderId,
            method=payment.paymentMethod, amount=payment.amount, status=payment.status,
            code=payment.transactionCode, paid_at=payment.paidAt.isoformat() if payment.paidAt else None)).inserted_primary_key[0]

    def update(self, payment: Payment) -> None:
        self.connection.execute(payments.update().where(payments.c.id == payment.paymentId).values(
            status=payment.status, paid_at=payment.paidAt.isoformat() if payment.paidAt else None))

