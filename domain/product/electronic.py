from dataclasses import dataclass

from domain.product.product import Product


@dataclass
class Electronic(Product):
    brand: str = ""
    model: str = ""
    warrantyMonths: int = 12
    powerWattage: int | None = None

    def searchableAttributes(self) -> list[str]:
        return [self.brand, self.model, str(self.warrantyMonths),
                "" if self.powerWattage is None else str(self.powerWattage)]
