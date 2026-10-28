from data.repository.product_repository import ProductRepository
from domain.product.product import Product
from domain.search.search_query import SearchQuery


class RetrievalService:
    def __init__(self, products: ProductRepository):
        self.products = products

    def retrieve(self, query: SearchQuery) -> list[Product]:
        return self.products.findRelevant(query)

