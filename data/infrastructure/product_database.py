from sqlalchemy import (create_engine, MetaData, Table, Column, Integer, String,
                        Text, ForeignKey, Numeric, CheckConstraint, event, inspect)

metadata = MetaData()
categories = Table("categories", metadata, Column("id", Integer, primary_key=True), Column("name", String, nullable=False))
products = Table("products", metadata,
    Column("id", Integer, primary_key=True), Column("name", String, nullable=False),
    Column("description", Text),
    Column("price", Numeric(14, 2), nullable=False), Column("status", String),
    Column("quantity_available", Integer, nullable=False), CheckConstraint("quantity_available >= 0"),
    Column("category_id", ForeignKey("categories.id"), nullable=False))
specifications = Table("product_specifications", metadata,
    Column("id", Integer, primary_key=True), Column("product_id", ForeignKey("products.id", ondelete="CASCADE")),
    Column("name", String), Column("value", String))
units = Table("product_units", metadata, Column("serial", String, primary_key=True),
    Column("product_id", ForeignKey("products.id", ondelete="CASCADE"), nullable=False))
electronics = Table("electronics", metadata,
    Column("product_id", ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("brand", String, nullable=False, server_default=""),
    Column("model", String, nullable=False, server_default=""),
    Column("warranty_months", Integer, nullable=False, server_default="12"),
    Column("power_wattage", Integer))
books = Table("books", metadata,
    Column("product_id", ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("author", String, nullable=False, server_default=""),
    Column("isbn", String, nullable=False, server_default=""),
    Column("publisher", String, nullable=False, server_default=""),
    Column("publication_year", Integer),
    Column("number_of_pages", Integer, nullable=False, server_default="0"),
    Column("cover_type", String, nullable=False, server_default="Paperback"))
fashions = Table("fashions", metadata,
    Column("product_id", ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("brand", String, nullable=False, server_default=""),
    Column("size", String, nullable=False, server_default=""),
    Column("color", String, nullable=False, server_default=""),
    Column("material", String, nullable=False, server_default=""),
    Column("gender", String, nullable=False, server_default="Unisex"))
furnitures = Table("furnitures", metadata,
    Column("product_id", ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("brand", String, server_default=""),
    Column("material", String, nullable=False, server_default=""),
    Column("dimensions", String, nullable=False, server_default=""),
    Column("weight_kg", Numeric(10, 2), nullable=False, server_default="0"),
    Column("assembly_required", Integer, nullable=False, server_default="0"))


class ProductDatabase:
    def __init__(self, url: str):
        self.engine = create_engine(url, connect_args={"check_same_thread": False, "timeout": 30})
        event.listen(self.engine, "connect", self._configure)

    @staticmethod
    def _configure(connection, record):
        connection.execute("PRAGMA foreign_keys=ON")

    def create(self) -> None:
        self._migrate_inventory()
        self._migrate_search_query()
        self._migrate_product_types()
        metadata.create_all(self.engine)

    def _migrate_product_types(self) -> None:
        with self.engine.begin() as connection:
            tables = set(inspect(connection).get_table_names())
            if "products" not in tables:
                return
            for table in (electronics, books, fashions, furnitures):
                table.create(connection, checkfirst=True)
            self._add_missing_subtype_columns(connection)
            product_columns = {column["name"] for column in inspect(connection).get_columns("products")}
            if "brand" not in product_columns and "model" not in product_columns:
                return
            brand_expression = "COALESCE(brand, '')" if "brand" in product_columns else "''"
            model_expression = "COALESCE(model, '')" if "model" in product_columns else "''"
            connection.exec_driver_sql(
                "INSERT OR IGNORE INTO electronics (product_id, brand, model, warranty_months) "
                f"SELECT id, {brand_expression}, {model_expression}, 12 FROM products")
            if "brand" in product_columns:
                connection.exec_driver_sql(
                    "UPDATE electronics SET brand = COALESCE((SELECT brand FROM products "
                    "WHERE products.id = electronics.product_id), '')")
            if "model" in product_columns:
                connection.exec_driver_sql(
                    "UPDATE electronics SET model = COALESCE((SELECT model FROM products "
                    "WHERE products.id = electronics.product_id), '')")

    @staticmethod
    def _add_missing_subtype_columns(connection) -> None:
        required = {
            "electronics": {"brand": "VARCHAR NOT NULL DEFAULT ''", "model": "VARCHAR NOT NULL DEFAULT ''",
                            "warranty_months": "INTEGER NOT NULL DEFAULT 12", "power_wattage": "INTEGER"},
            "books": {"author": "VARCHAR NOT NULL DEFAULT ''", "isbn": "VARCHAR NOT NULL DEFAULT ''",
                      "publisher": "VARCHAR NOT NULL DEFAULT ''", "publication_year": "INTEGER",
                      "number_of_pages": "INTEGER NOT NULL DEFAULT 0",
                      "cover_type": "VARCHAR NOT NULL DEFAULT 'Paperback'"},
            "fashions": {"brand": "VARCHAR NOT NULL DEFAULT ''", "size": "VARCHAR NOT NULL DEFAULT ''",
                         "color": "VARCHAR NOT NULL DEFAULT ''", "material": "VARCHAR NOT NULL DEFAULT ''",
                         "gender": "VARCHAR NOT NULL DEFAULT 'Unisex'"},
            "furnitures": {"brand": "VARCHAR DEFAULT ''", "material": "VARCHAR NOT NULL DEFAULT ''",
                           "dimensions": "VARCHAR NOT NULL DEFAULT ''",
                           "weight_kg": "NUMERIC(10, 2) NOT NULL DEFAULT 0",
                           "assembly_required": "INTEGER NOT NULL DEFAULT 0"},
        }
        for table_name, columns in required.items():
            existing = {column["name"] for column in inspect(connection).get_columns(table_name)}
            for column_name, definition in columns.items():
                if column_name not in existing:
                    connection.exec_driver_sql(
                        f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")

    def _migrate_search_query(self) -> None:
        with self.engine.begin() as connection:
            tables = set(inspect(connection).get_table_names())
            if "search_queries" not in tables:
                return
            columns = {column["name"] for column in inspect(connection).get_columns("search_queries")}
            if "search_criteria" in columns:
                connection.exec_driver_sql("ALTER TABLE search_queries DROP COLUMN search_criteria")

    def _migrate_inventory(self) -> None:
        with self.engine.begin() as connection:
            tables = set(inspect(connection).get_table_names())
            if "products" not in tables:
                return
            product_columns = {column["name"] for column in inspect(connection).get_columns("products")}
            if "quantity_available" not in product_columns:
                connection.exec_driver_sql(
                    "ALTER TABLE products ADD COLUMN quantity_available INTEGER NOT NULL DEFAULT 0")
            if "inventories" in tables:
                connection.exec_driver_sql(
                    "UPDATE products SET quantity_available = COALESCE((SELECT quantity FROM inventories "
                    "WHERE inventories.product_id = products.id), quantity_available)")
            if "product_units" in tables:
                unit_columns = {column["name"] for column in inspect(connection).get_columns("product_units")}
                if "inventory_id" in unit_columns:
                    connection.exec_driver_sql("DROP TABLE IF EXISTS product_units_migrated")
                    connection.exec_driver_sql(
                        "CREATE TABLE product_units_migrated (serial VARCHAR PRIMARY KEY, "
                        "product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE)")
                    if "inventories" in tables:
                        connection.exec_driver_sql(
                            "INSERT INTO product_units_migrated (serial, product_id) "
                            "SELECT product_units.serial, inventories.product_id FROM product_units "
                            "JOIN inventories ON inventories.id = product_units.inventory_id")
                    connection.exec_driver_sql("DROP TABLE product_units")
                    connection.exec_driver_sql("ALTER TABLE product_units_migrated RENAME TO product_units")
            if "inventories" in tables:
                connection.exec_driver_sql("DROP TABLE inventories")

