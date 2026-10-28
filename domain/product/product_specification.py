from dataclasses import dataclass


@dataclass
class ProductSpecification:
    specificationId: int
    specName: str
    specValue: str

