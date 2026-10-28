from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from domain.customer.customer import Customer
from domain.product.product import Product


class InteractionType(StrEnum):
    VIEW = "VIEW"
    CLICK = "CLICK"
    ADD_TO_CART = "ADD_TO_CART"
    PURCHASE = "PURCHASE"


@dataclass
class Interaction:
    interactionId: int
    interactionType: InteractionType
    interactedAt: datetime
    customer: Customer
    product: Product

