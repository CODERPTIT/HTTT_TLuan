from dataclasses import dataclass
from domain.product.product import Product


@dataclass
class OrderItem:
    orderItemId: int
    quantity: int
    product: Product

