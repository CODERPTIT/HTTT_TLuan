from datetime import datetime, timezone

from sqlalchemy import select

from data.infrastructure.order_database import (customers, orders, payments, shipments,
                                                shipping_providers, users)


class ShippingProviderRepository:
    def __init__(self, connection):
        self.connection = connection

    def shipments(self, provider_id: int):
        self._require_provider(provider_id)
        return self.connection.execute(select(
            orders.c.id.label("order_id"), orders.c.status.label("order_status"), orders.c.date,
            orders.c.address, orders.c.phone, users.c.full_name.label("customer"),
            shipments.c.tracking, shipments.c.status.label("shipment_status"),
            shipments.c.estimated, shipments.c.delivered)
            .join(shipments, shipments.c.order_id == orders.c.id)
            .join(customers, orders.c.customer_id == customers.c.id)
            .join(users, customers.c.id == users.c.id)
            .where(shipments.c.shipping_provider_id == provider_id)
            .order_by(orders.c.id.desc())).mappings().all()

    def mark_out_for_delivery(self, provider_id: int, order_id: int) -> None:
        self._require_provider(provider_id)
        changed = self.connection.execute(shipments.update().where(
            shipments.c.order_id == order_id,
            shipments.c.shipping_provider_id == provider_id,
            shipments.c.status == "SHIPPED").values(status="OUT_FOR_DELIVERY"))
        if not changed.rowcount:
            raise ValueError("Only an assigned shipped order can be taken out for delivery")

    def mark_delivered(self, provider_id: int, order_id: int) -> None:
        self._require_provider(provider_id)
        delivered_at = datetime.now(timezone.utc).isoformat()
        changed = self.connection.execute(shipments.update().where(
            shipments.c.order_id == order_id,
            shipments.c.shipping_provider_id == provider_id,
            shipments.c.status == "OUT_FOR_DELIVERY").values(
                status="DELIVERED", delivered=delivered_at))
        if not changed.rowcount:
            raise ValueError("Only an assigned order out for delivery can be marked delivered")
        self.connection.execute(orders.update().where(
            orders.c.id == order_id, orders.c.status == "SHIPPED").values(status="DELIVERED"))
        self.connection.execute(payments.update().where(
            payments.c.order_id == order_id, payments.c.status == "PENDING").values(
                status="PAID", paid_at=delivered_at))

    def _require_provider(self, provider_id: int) -> None:
        if not self.connection.execute(select(shipping_providers.c.id).where(
                shipping_providers.c.id == provider_id)).first():
            raise LookupError("Shipping provider profile not found")
