from sqlalchemy import select, delete
from domain.product.product import Product, ProductStatus
from domain.product.category import Category
from domain.product.product_specification import ProductSpecification
from domain.product.product_unit import ProductUnit
from domain.product.electronic import Electronic
from domain.product.book import Book
from domain.product.fashion import Fashion
from domain.product.furniture import Furniture
from data.infrastructure.product_database import (products, categories, specifications, units,
                                                  electronics, books, fashions, furnitures)


class ProductRepository:
    def __init__(self, connection, image_storage=None, vector_index=None):
        self.connection = connection
        self.image_storage = image_storage
        self.vector_index = vector_index

    def findById(self, productId: int) -> Product:
        row = self.connection.execute(select(products).where(products.c.id == productId)).mappings().first()
        if row is None:
            raise LookupError("Product not found")
        category = self.connection.execute(select(categories).where(categories.c.id == row["category_id"])).mappings().one()
        serials = self.connection.execute(select(units.c.serial).where(units.c.product_id == productId)).scalars()
        specs = self.connection.execute(select(specifications).where(specifications.c.product_id == productId)).mappings()
        common = dict(productId=row["id"], productName=row["name"], description=row["description"] or "",
                      price=row["price"], status=ProductStatus(row["status"]),
                      category=Category(category["id"], category["name"]),
                      quantityAvailable=row["quantity_available"],
                      units=[ProductUnit(serial) for serial in serials],
                      specifications=[ProductSpecification(spec["id"], spec["name"], spec["value"])
                                      for spec in specs])
        electronic = self._details(electronics, productId)
        if electronic:
            return Electronic(**common, brand=electronic["brand"], model=electronic["model"],
                              warrantyMonths=electronic["warranty_months"],
                              powerWattage=electronic["power_wattage"])
        book = self._details(books, productId)
        if book:
            return Book(**common, author=book["author"], isbn=book["isbn"], publisher=book["publisher"],
                        publicationYear=book["publication_year"], numberOfPages=book["number_of_pages"],
                        coverType=book["cover_type"])
        fashion = self._details(fashions, productId)
        if fashion:
            return Fashion(**common, brand=fashion["brand"], size=fashion["size"], color=fashion["color"],
                           material=fashion["material"], gender=fashion["gender"])
        furniture = self._details(furnitures, productId)
        if furniture:
            return Furniture(**common, brand=furniture["brand"] or "", material=furniture["material"],
                             dimensions=furniture["dimensions"], weightKg=furniture["weight_kg"],
                             assemblyRequired=bool(furniture["assembly_required"]))
        raise LookupError(f"Missing subtype details for product {productId}")

    def _details(self, table, productId: int):
        return self.connection.execute(
            select(table).where(table.c.product_id == productId)).mappings().first()

    def findRelevant(self, query) -> list[Product]:
        return [self.findById(identity) for identity in self.connection.execute(select(products.c.id)).scalars()]

    def findByCategory(self, categoryId: int) -> list[Product]:
        return [product for product in self.findRelevant(None) if product.category.categoryId == categoryId]

    def findEligibleProducts(self) -> list[Product]:
        return [product for product in self.findRelevant(None)
                if product.status == ProductStatus.ACTIVE and product.isAvailable(1)]

    def save(self, product: Product) -> None:
        self.connection.execute(products.insert().values(id=product.productId, name=product.productName,
            description=product.description, price=product.price, status=product.status,
            quantity_available=product.quantityAvailable,
            category_id=product.category.categoryId))
        self._save_subtype(product)
        for specification in product.specifications:
            self.connection.execute(specifications.insert().values(product_id=product.productId,
                name=specification.specName, value=specification.specValue))
        for unit in product.units:
            self.connection.execute(units.insert().values(serial=unit.serialNumber, product_id=product.productId))

    def update(self, product: Product) -> None:
        self.connection.execute(products.update().where(products.c.id == product.productId).values(
            name=product.productName, description=product.description, price=product.price,
            status=product.status, quantity_available=product.quantityAvailable,
            category_id=product.category.categoryId))
        for table in (electronics, books, fashions, furnitures):
            self.connection.execute(delete(table).where(table.c.product_id == product.productId))
        self._save_subtype(product)
        self.connection.execute(delete(specifications).where(specifications.c.product_id == product.productId))
        for specification in product.specifications:
            self.connection.execute(specifications.insert().values(product_id=product.productId,
                name=specification.specName, value=specification.specValue))
        self.connection.execute(delete(units).where(units.c.product_id == product.productId))
        for unit in product.units:
            self.connection.execute(units.insert().values(serial=unit.serialNumber, product_id=product.productId))

    def updateStock(self, product: Product) -> None:
        self.connection.execute(products.update().where(products.c.id == product.productId)
                                .values(quantity_available=product.quantityAvailable))

    def _save_subtype(self, product: Product) -> None:
        if isinstance(product, Electronic):
            self.connection.execute(electronics.insert().values(product_id=product.productId,
                brand=product.brand, model=product.model, warranty_months=product.warrantyMonths,
                power_wattage=product.powerWattage))
        elif isinstance(product, Book):
            self.connection.execute(books.insert().values(product_id=product.productId, author=product.author,
                isbn=product.isbn, publisher=product.publisher, publication_year=product.publicationYear,
                number_of_pages=product.numberOfPages, cover_type=product.coverType))
        elif isinstance(product, Fashion):
            self.connection.execute(fashions.insert().values(product_id=product.productId, brand=product.brand,
                size=product.size, color=product.color, material=product.material, gender=product.gender))
        elif isinstance(product, Furniture):
            self.connection.execute(furnitures.insert().values(product_id=product.productId, brand=product.brand,
                material=product.material, dimensions=product.dimensions, weight_kg=product.weightKg,
                assembly_required=int(product.assemblyRequired)))
        else:
            raise ValueError("Product must be Electronic, Book, Fashion, or Furniture")

    def saveImage(self, content: bytes, filename: str, content_type: str) -> str:
        return self.image_storage.save(content, filename, content_type)

    def cropImage(self, reference: str, box: list[float]) -> str:
        return self.image_storage.crop(reference, box)

    def imagePath(self, reference: str):
        return self.image_storage.resolve(reference)

    def indexVector(self, productId: int, vector: list[float]) -> None:
        self.vector_index.store(productId, vector)

    def searchVectors(self, vector: list[float]) -> list[tuple[int, float]]:
        return self.vector_index.search(vector)

