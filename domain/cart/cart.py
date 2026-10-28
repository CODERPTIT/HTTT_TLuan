from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from domain.cart.cart_item import CartItem
from domain.product.product import Product


@dataclass
class Cart:
    cartId: int
    customerId: int
    createdAt: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    items: list[CartItem] = field(default_factory=list)

    def findItem(self, product: Product) -> CartItem | None:
        return next((item for item in self.items if item.product.productId == product.productId), None)

    def addItem(self, product: Product, quantity: int) -> None:
        if type(quantity) is not int or quantity <= 0:
            raise ValueError("Quantity must be a positive integer")
        item = self.findItem(product)
        if item:
            item.quantity += quantity
        else:
            self.items.append(CartItem(0, quantity, product))

    def removeItem(self, product: Product) -> None:
        self.items = [item for item in self.items if item.product.productId != product.productId]

    def updateQuantity(self, product: Product, quantity: int) -> None:
        if type(quantity) is not int or quantity <= 0:
            raise ValueError("Quantity must be a positive integer")
        item = self.findItem(product)
        if item is None:
            raise ValueError("Product is not in your cart")
        item.quantity = quantity

    def calculateTotal(self) -> Decimal:
        return sum((item.product.price * item.quantity for item in self.items), Decimal("0"))

    def isEmpty(self) -> bool:
        return not self.items

