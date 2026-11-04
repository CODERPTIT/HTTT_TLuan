from sqlalchemy import select

from data.infrastructure.order_database import customers, users
from domain.customer.customer import Customer


class CustomerRepository:
    def __init__(self, connection):
        self.connection = connection

    def findById(self, customerId: int) -> Customer:
        row = self.connection.execute(select(
            customers.c.id, customers.c.delivery_address, users.c.full_name, users.c.email,
            users.c.phone, users.c.role, users.c.active,
        ).join(users, users.c.id == customers.c.id).where(customers.c.id == customerId)).mappings().first()
        if row is None:
            raise LookupError("Customer not found")
        return Customer(row["id"], row["full_name"], row["email"], row["phone"] or "",
                        row["role"], bool(row["active"]), row["delivery_address"] or "")
