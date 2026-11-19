from dataclasses import dataclass
from decimal import Decimal

from domain.product.product import Product


@dataclass
class Furniture(Product):
    brand: str = ""
    material: str = ""
    dimensions: str = ""
    weightKg: Decimal = Decimal(0)
    assemblyRequired: bool = False

    def searchableAttributes(self) -> list[str]:
        return [self.brand, self.material, self.dimensions, str(self.weightKg),
                "assembly required" if self.assemblyRequired else "assembled"]
