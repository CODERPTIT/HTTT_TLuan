from dataclasses import dataclass

from domain.user.user import User


@dataclass
class Customer(User):
    deliveryAddress: str = ""

    @property
    def customerId(self) -> int:
        return self.userId

