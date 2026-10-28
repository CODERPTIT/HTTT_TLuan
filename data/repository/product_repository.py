from sqlalchemy import select, delete
from domain.product.product import Product, ProductStatus
from domain.product.category import Category
from domain.product.product_specification import ProductSpecification
from domain.product.product_unit import ProductUnit
from data.infrastructure.product_database import products, categories, specifications, units


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
        return Product(row["id"], row["name"], row["brand"], row["model"], row["description"],
                       row["price"], ProductStatus(row["status"]), Category(category["id"], category["name"]),
                       row["quantity_available"], [ProductUnit(serial) for serial in serials],
                       [ProductSpecification(spec["id"], spec["name"], spec["value"]) for spec in specs])

    def findRelevant(self, query) -> list[Product]:
        return [self.findById(identity) for identity in self.connection.execute(select(products.c.id)).scalars()]

    def findByCategory(self, categoryId: int) -> list[Product]:
        return [product for product in self.findRelevant(None) if product.category.categoryId == categoryId]

    def findEligibleProducts(self) -> list[Product]:
        return [product for product in self.findRelevant(None)
                if product.status == ProductStatus.ACTIVE and product.isAvailable(1)]

    def save(self, product: Product) -> None:
        self.connection.execute(products.insert().values(id=product.productId, name=product.productName,
            brand=product.brand, model=product.model, description=product.description,
            price=product.price, status=product.status, quantity_available=product.quantityAvailable,
            category_id=product.category.categoryId))
        for specification in product.specifications:
            self.connection.execute(specifications.insert().values(product_id=product.productId,
                name=specification.specName, value=specification.specValue))
        for unit in product.units:
            self.connection.execute(units.insert().values(serial=unit.serialNumber, product_id=product.productId))

    def update(self, product: Product) -> None:
        self.connection.execute(products.update().where(products.c.id == product.productId).values(
            name=product.productName, brand=product.brand, model=product.model, description=product.description,
            price=product.price, status=product.status, quantity_available=product.quantityAvailable,
            category_id=product.category.categoryId))
        self.connection.execute(delete(specifications).where(specifications.c.product_id == product.productId))
        for specification in product.specifications:
            self.connection.execute(specifications.insert().values(product_id=product.productId,
                name=specification.specName, value=specification.specValue))
        self.connection.execute(delete(units).where(units.c.product_id == product.productId))
        for unit in product.units:
            self.connection.execute(units.insert().values(serial=unit.serialNumber, product_id=product.productId))

    def _updateStock(self, product: Product) -> None:
        self.connection.execute(products.update().where(products.c.id == product.productId)
                                .values(quantity_available=product.quantityAvailable))

    def _saveImage(self, content: bytes, filename: str, content_type: str) -> str:
        return self.image_storage.save(content, filename, content_type)

    def _imagePath(self, reference: str):
        return self.image_storage.resolve(reference)

    def _indexVector(self, productId: int, vector: list[float]) -> None:
        self.vector_index.store(productId, vector)

    def _searchVectors(self, vector: list[float]) -> list[tuple[int, float]]:
        return self.vector_index.search(vector)

