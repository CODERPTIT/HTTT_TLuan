from sqlalchemy import (create_engine, MetaData, Table, Column, Integer, String,
                        Text, ForeignKey, Numeric, CheckConstraint, event, inspect)

metadata = MetaData()
categories = Table("categories", metadata, Column("id", Integer, primary_key=True), Column("name", String, nullable=False))
products = Table("products", metadata,
    Column("id", Integer, primary_key=True), Column("name", String, nullable=False),
    Column("brand", String), Column("model", String), Column("description", Text),
    Column("price", Numeric(14, 2), nullable=False), Column("status", String),
    Column("quantity_available", Integer, nullable=False), CheckConstraint("quantity_available >= 0"),
    Column("category_id", ForeignKey("categories.id"), nullable=False))
specifications = Table("product_specifications", metadata,
    Column("id", Integer, primary_key=True), Column("product_id", ForeignKey("products.id", ondelete="CASCADE")),
    Column("name", String), Column("value", String))
units = Table("product_units", metadata, Column("serial", String, primary_key=True),
    Column("product_id", ForeignKey("products.id", ondelete="CASCADE"), nullable=False))


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
        metadata.create_all(self.engine)

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

