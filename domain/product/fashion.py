from dataclasses import dataclass

from domain.product.product import Product


@dataclass
class Fashion(Product):
    brand: str = ""
    size: str = ""
    color: str = ""
    material: str = ""
    gender: str = "Unisex"

    def searchableAttributes(self) -> list[str]:
        return [self.brand, self.size, self.color, self.material, self.gender]
