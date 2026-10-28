from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from domain.product.category import Category
from domain.product.product_unit import ProductUnit
from domain.product.product_specification import ProductSpecification


class ProductStatus(StrEnum):
    ACTIVE = "ACTIVE"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    DISCONTINUED = "DISCONTINUED"


@dataclass
class Product:
    productId: int
    productName: str
    brand: str
    model: str
    description: str
    price: Decimal
    status: ProductStatus
    category: Category
    quantityAvailable: int
    units: list[ProductUnit] = field(default_factory=list)
    specifications: list[ProductSpecification] = field(default_factory=list)

    def isAvailable(self, quantity: int) -> bool:
        return isinstance(quantity, int) and not isinstance(quantity, bool) and 0 < quantity <= self.quantityAvailable

    def reserve(self, quantity: int) -> bool:
        if not self.isAvailable(quantity):
            raise ValueError("Insufficient stock or invalid quantity")
        self.quantityAvailable -= quantity
        return True

    def release(self, quantity: int) -> None:
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer")
        self.quantityAvailable += quantity

    def searchableText(self) -> str:
        return " ".join([self.productName, self.brand, self.model, self.description,
                         self.category.categoryName] +
                        [spec.specName + " " + spec.specValue for spec in self.specifications])

