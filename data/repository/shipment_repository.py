from datetime import datetime
from sqlalchemy import select
from domain.order.shipment import Shipment, ShipmentStatus
from data.infrastructure.order_database import shipments


class ShipmentRepository:
    def __init__(self, connection):
        self.connection = connection

    def _find(self, statement) -> Shipment:
        row = self.connection.execute(statement).mappings().first()
        if row is None:
            raise LookupError("Shipment not available yet")
        return Shipment(row["tracking"], ShipmentStatus(row["status"]), row["carrier"],
            datetime.fromisoformat(row["estimated"]), datetime.fromisoformat(row["delivered"]) if row["delivered"] else None,
            row["order_id"])

    def findByOrder(self, orderId: int) -> Shipment:
        return self._find(select(shipments).where(shipments.c.order_id == orderId))

    def findByTrackingNumber(self, trackingNumber: str) -> Shipment:
        return self._find(select(shipments).where(shipments.c.tracking == trackingNumber))

    def save(self, shipment: Shipment) -> None:
        if shipment._orderId <= 0:
            raise ValueError("Shipment must be associated with an order")
        self.connection.execute(shipments.insert().values(tracking=shipment.trackingNumber, order_id=shipment._orderId,
            status=shipment.status, carrier=shipment.carrier, estimated=shipment.estimatedDeliveryDate.isoformat(),
            delivered=shipment.deliveredAt.isoformat() if shipment.deliveredAt else None))

    def update(self, shipment: Shipment) -> None:
        self.connection.execute(shipments.update().where(shipments.c.tracking == shipment.trackingNumber).values(
            status=shipment.status, delivered=shipment.deliveredAt.isoformat() if shipment.deliveredAt else None))

