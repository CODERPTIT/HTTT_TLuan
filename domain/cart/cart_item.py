from dataclasses import dataclass
from domain.product.product import Product


@dataclass
class CartItem:
    cartItemId: int
    quantity: int
    product: Product

