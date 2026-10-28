from dataclasses import dataclass
from decimal import Decimal
from domain.product.product import Product


@dataclass
class SearchResult:
    rank: int
    relevanceScore: Decimal
    product: Product

