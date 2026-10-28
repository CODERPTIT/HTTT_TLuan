from datetime import datetime, timezone
from sqlalchemy import select
from domain.customer.customer import Customer
from domain.interaction.interaction import Interaction, InteractionType
from data.infrastructure.order_database import customers, interactions


class InteractionRepository:
    def __init__(self, connection, products):
        self.connection = connection
        self.products = products

    def _customer(self, customerId: int) -> Customer:
        row = self.connection.execute(select(customers).where(customers.c.id == customerId)).mappings().first()
        if row is None:
            raise LookupError("Customer not found")
        return Customer(row["id"], row["name"], row["email"], row["phone"], row["address"])

    def _find(self, statement) -> list[Interaction]:
        return [Interaction(row["id"], InteractionType(row["type"]), datetime.fromisoformat(row["at"]),
                self._customer(row["customer_id"]), self.products.findById(row["product_id"]))
                for row in self.connection.execute(statement).mappings()]

    def findByCustomer(self, customerId: int) -> list[Interaction]:
        return self._find(select(interactions).where(interactions.c.customer_id == customerId))

    def findByProduct(self, productId: int) -> list[Interaction]:
        return self._find(select(interactions).where(interactions.c.product_id == productId))

    def save(self, interaction: Interaction) -> None:
        interaction.interactionId = self.connection.execute(interactions.insert().values(
            customer_id=interaction.customer.customerId, product_id=interaction.product.productId,
            type=interaction.interactionType, at=interaction.interactedAt.isoformat())).inserted_primary_key[0]

    def _record(self, customerId: int, product, kind: InteractionType) -> None:
        self.save(Interaction(0, kind, datetime.now(timezone.utc), self._customer(customerId), product))

