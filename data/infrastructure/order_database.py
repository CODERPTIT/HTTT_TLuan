from datetime import datetime, timezone

from sqlalchemy import Table, Column, Integer, String, Text, ForeignKey, Numeric, CheckConstraint, inspect
from data.infrastructure.product_database import metadata

users = Table("users", metadata, Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False, unique=True), Column("password_hash", String, nullable=False),
    Column("role", String, nullable=False), Column("full_name", String, nullable=False),
    Column("phone", String), Column("active", Integer, nullable=False, default=1),
    Column("created_at", String, nullable=False))
customers = Table("customers", metadata,
    Column("id", ForeignKey("users.id", ondelete="CASCADE", deferrable=True, initially="DEFERRED"), primary_key=True),
    Column("delivery_address", Text))
staff = Table("staff", metadata,
    Column("id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("employee_code", String, nullable=False, unique=True), Column("department", String, nullable=False),
    Column("position", String, nullable=False))
shipping_providers = Table("shipping_providers", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("users.id"), nullable=False, unique=True),
    Column("provider_code", String, nullable=False, unique=True),
    Column("provider_name", String, nullable=False),
    Column("support_email", String, nullable=False),
    Column("support_phone", String), Column("address", Text),
    Column("active", Integer, nullable=False, default=1))
interactions = Table("interactions", metadata, Column("id", Integer, primary_key=True),
    Column("customer_id", ForeignKey("customers.id")), Column("product_id", ForeignKey("products.id")),
    Column("type", String), Column("at", String))
search_queries = Table("search_queries", metadata, Column("id", Integer, primary_key=True),
    Column("customer_id", ForeignKey("customers.id"), nullable=False),
    Column("created_at", String, nullable=False), Column("type", String, nullable=False))
text_queries = Table("text_queries", metadata,
    Column("search_query_id", ForeignKey("search_queries.id", ondelete="CASCADE"), primary_key=True),
    Column("query_text", Text, nullable=False))
image_queries = Table("image_queries", metadata,
    Column("search_query_id", ForeignKey("search_queries.id", ondelete="CASCADE"), primary_key=True),
    Column("image_reference", Text, nullable=False))
voice_queries = Table("voice_queries", metadata,
    Column("search_query_id", ForeignKey("search_queries.id", ondelete="CASCADE"), primary_key=True),
    Column("transcribed_text", Text, nullable=False), Column("audio_reference", Text, nullable=False))
search_results = Table("search_results", metadata,
    Column("search_query_id", ForeignKey("search_queries.id", ondelete="CASCADE"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True),
    Column("rank", Integer, nullable=False), Column("relevance_score", Numeric(10, 6), nullable=False))
carts = Table("carts", metadata, Column("id", Integer, primary_key=True),
    Column("customer_id", ForeignKey("customers.id"), unique=True), Column("created_at", String))
cart_items = Table("cart_items", metadata, Column("id", Integer, primary_key=True),
    Column("cart_id", ForeignKey("carts.id", ondelete="CASCADE")), Column("product_id", ForeignKey("products.id")),
    Column("quantity", Integer), CheckConstraint("quantity > 0"))
orders = Table("orders", metadata, Column("id", Integer, primary_key=True),
    Column("customer_id", ForeignKey("customers.id")), Column("address", Text),
    Column("phone", String), Column("date", String), Column("status", String))
order_items = Table("order_items", metadata, Column("id", Integer, primary_key=True),
    Column("order_id", ForeignKey("orders.id", ondelete="CASCADE")), Column("product_id", ForeignKey("products.id")),
    Column("quantity", Integer), Column("price_snapshot", Numeric(14, 2)), CheckConstraint("quantity > 0"))
payments = Table("payments", metadata, Column("id", Integer, primary_key=True),
    Column("order_id", ForeignKey("orders.id"), unique=True), Column("method", String),
    Column("amount", Numeric(14, 2)), Column("status", String), Column("code", String), Column("paid_at", String))
shipments = Table("shipments", metadata, Column("tracking", String, primary_key=True),
    Column("order_id", ForeignKey("orders.id"), unique=True), Column("status", String),
    Column("carrier", String), Column("estimated", String), Column("delivered", String),
    Column("shipping_provider_id", ForeignKey("shipping_providers.id")))


class OrderDatabase:
    def __init__(self, engine):
        self.engine = engine

    def transaction(self):
        return self.engine.begin()

    def migrate_identity(self) -> None:
        """Migrate the former accounts/customer profile split to class-table inheritance."""
        if "accounts" not in inspect(self.engine).get_table_names():
            return
        raw = self.engine.raw_connection()
        try:
            cursor = raw.cursor()
            cursor.execute("PRAGMA foreign_keys=OFF")
            cursor.execute("BEGIN IMMEDIATE")
            account_rows = cursor.execute(
                "SELECT id, email, password_hash, role, customer_id, active FROM accounts ORDER BY id"
            ).fetchall()
            customer_rows = cursor.execute(
                "SELECT id, name, email, phone, address FROM customers ORDER BY id"
            ).fetchall()
            customer_by_id = {row[0]: row for row in customer_rows}
            now = datetime.now(timezone.utc).isoformat()
            used_ids = {row[0] for row in customer_rows}
            next_staff_id = max(used_ids, default=0) + 1

            for _, email, password_hash, role, customer_id, active in account_rows:
                if role == "CUSTOMER" and customer_id in customer_by_id:
                    identity, name, legacy_email, phone, _ = customer_by_id[customer_id]
                    cursor.execute(
                        "INSERT OR IGNORE INTO users "
                        "(id, email, password_hash, role, full_name, phone, active, created_at) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (identity, email or legacy_email, password_hash, role, name, phone or "", active, now),
                    )
                    continue
                while next_staff_id in used_ids:
                    next_staff_id += 1
                identity = next_staff_id
                next_staff_id += 1
                used_ids.add(identity)
                name = role.replace("_", " ").title()
                cursor.execute(
                    "INSERT OR IGNORE INTO users "
                    "(id, email, password_hash, role, full_name, phone, active, created_at) "
                    "VALUES (?, ?, ?, ?, ?, '', ?, ?)",
                    (identity, email, password_hash, role, name, active, now),
                )
                cursor.execute(
                    "INSERT OR IGNORE INTO staff (id, employee_code, department, position) VALUES (?, ?, ?, ?)",
                    (identity, f"ABC-{identity:04}", self._department(role), name),
                )

            cursor.execute("DROP TABLE accounts")
            cursor.execute(
                "CREATE TABLE customers_migrated ("
                "id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED, "
                "delivery_address TEXT)"
            )
            cursor.execute(
                "INSERT INTO customers_migrated (id, delivery_address) SELECT id, address FROM customers"
            )
            cursor.execute("DROP TABLE customers")
            cursor.execute("ALTER TABLE customers_migrated RENAME TO customers")
            raw.commit()
            cursor.execute("PRAGMA foreign_keys=ON")
        except Exception:
            raw.rollback()
            raise
        finally:
            raw.close()

    def migrate_shipping_provider(self) -> None:
        """Keep providers independent while assigning one unique representative user."""
        raw = self.engine.raw_connection()
        try:
            cursor = raw.cursor()
            cursor.execute("PRAGMA foreign_keys=OFF")
            cursor.execute("BEGIN IMMEDIATE")
            tables = {row[0] for row in cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
            user_columns = {row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()}
            if "shipping_providers" in tables:
                provider_columns = {row[1] for row in cursor.execute(
                    "PRAGMA table_info(shipping_providers)").fetchall()}
                if "user_id" not in provider_columns:
                    support_email = ("support_email" if "support_email" in provider_columns
                                     else "'shipping@abc.test'")
                    support_phone = "support_phone" if "support_phone" in provider_columns else "''"
                    address = "address" if "address" in provider_columns else "''"
                    active = "active" if "active" in provider_columns else "1"
                    representative = (
                        "COALESCE((SELECT users.id FROM users WHERE "
                        "users.shipping_provider_id = shipping_providers.id LIMIT 1), "
                        "(SELECT users.id FROM users WHERE users.id = shipping_providers.id "
                        "AND users.role = 'SHIPPING_PROVIDER' LIMIT 1))"
                        if "shipping_provider_id" in user_columns else
                        "(SELECT users.id FROM users WHERE users.id = shipping_providers.id "
                        "AND users.role = 'SHIPPING_PROVIDER' LIMIT 1)"
                    )
                    cursor.execute(
                        "CREATE TABLE shipping_providers_migrated ("
                        "id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL UNIQUE REFERENCES users(id), "
                        "provider_code VARCHAR NOT NULL UNIQUE, provider_name VARCHAR NOT NULL, "
                        "support_email VARCHAR NOT NULL, support_phone VARCHAR, address TEXT, "
                        "active INTEGER NOT NULL DEFAULT 1)"
                    )
                    cursor.execute(
                        "INSERT INTO shipping_providers_migrated "
                        "(id, user_id, provider_code, provider_name, support_email, support_phone, address, active) "
                        f"SELECT id, {representative}, provider_code, provider_name, {support_email}, "
                        f"{support_phone}, {address}, {active} FROM shipping_providers"
                    )
                    cursor.execute("DROP TABLE shipping_providers")
                    cursor.execute("ALTER TABLE shipping_providers_migrated RENAME TO shipping_providers")
            if "shipping_provider_id" in user_columns:
                cursor.execute(
                    "CREATE TABLE users_migrated ("
                    "id INTEGER PRIMARY KEY, email VARCHAR NOT NULL UNIQUE, password_hash VARCHAR NOT NULL, "
                    "role VARCHAR NOT NULL, full_name VARCHAR NOT NULL, phone VARCHAR, "
                    "active INTEGER NOT NULL DEFAULT 1, created_at VARCHAR NOT NULL)"
                )
                cursor.execute(
                    "INSERT INTO users_migrated "
                    "(id, email, password_hash, role, full_name, phone, active, created_at) "
                    "SELECT id, email, password_hash, role, full_name, phone, active, created_at FROM users"
                )
                cursor.execute("DROP TABLE users")
                cursor.execute("ALTER TABLE users_migrated RENAME TO users")
            shipment_columns = {row[1] for row in cursor.execute("PRAGMA table_info(shipments)").fetchall()}
            if "shipping_provider_id" not in shipment_columns:
                cursor.execute(
                    "ALTER TABLE shipments ADD COLUMN shipping_provider_id INTEGER "
                    "REFERENCES shipping_providers(id)"
                )
            shipment_foreign_tables = {row[2] for row in cursor.execute(
                "PRAGMA foreign_key_list(shipments)").fetchall()}
            if "shipping_providers_legacy" in shipment_foreign_tables:
                cursor.execute(
                    "CREATE TABLE shipments_migrated ("
                    "tracking VARCHAR PRIMARY KEY, order_id INTEGER UNIQUE REFERENCES orders(id), "
                    "status VARCHAR, carrier VARCHAR, estimated VARCHAR, delivered VARCHAR, "
                    "shipping_provider_id INTEGER REFERENCES shipping_providers(id))"
                )
                cursor.execute(
                    "INSERT INTO shipments_migrated "
                    "(tracking, order_id, status, carrier, estimated, delivered, shipping_provider_id) "
                    "SELECT tracking, order_id, status, carrier, estimated, delivered, shipping_provider_id "
                    "FROM shipments"
                )
                cursor.execute("DROP TABLE shipments")
                cursor.execute("ALTER TABLE shipments_migrated RENAME TO shipments")
            raw.commit()
            cursor.execute("PRAGMA foreign_keys=ON")
        except Exception:
            raw.rollback()
            raise
        finally:
            raw.close()

    @staticmethod
    def _department(role: str) -> str:
        return {
            "ADMINISTRATOR": "Administration",
            "SALES_STAFF": "Sales",
            "WAREHOUSE_STAFF": "Warehouse",
            "MANAGER": "Management",
        }.get(role, "Operations")

