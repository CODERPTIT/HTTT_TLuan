from sqlalchemy import inspect

from domain.product.book import Book
from domain.product.electronic import Electronic
from domain.product.fashion import Fashion
from domain.product.furniture import Furniture


def test_product_schema_uses_class_table_inheritance(container):
    inspector = inspect(container.database.engine)
    tables = set(inspector.get_table_names())
    assert {"electronics", "books", "fashions", "furnitures"} <= tables
    product_columns = {column["name"] for column in inspector.get_columns("products")}
    assert "brand" not in product_columns
    assert "model" not in product_columns
    for table_name in ("electronics", "books", "fashions", "furnitures"):
        foreign_keys = inspector.get_foreign_keys(table_name)
        assert any(key["referred_table"] == "products" for key in foreign_keys)


def test_repository_returns_all_four_product_subtypes(services):
    catalog = services.search.catalog()
    assert {type(product) for product in catalog} == {Electronic, Book, Fashion, Furniture}
    assert {product.category.categoryName for product in catalog} == {
        "Electronic", "Book", "Fashion", "Furniture"
    }
    assert all(product.searchableText() for product in catalog)
