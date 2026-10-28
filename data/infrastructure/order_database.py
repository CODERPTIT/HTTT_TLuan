from sqlalchemy import Table, Column, Integer, String, Text, ForeignKey, Numeric, CheckConstraint
from data.infrastructure.product_database import metadata

customers = Table("customers", metadata, Column("id", Integer, primary_key=True),
    Column("name", String), Column("email", String), Column("phone", String), Column("address", Text))
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
    Column("carrier", String), Column("estimated", String), Column("delivered", String))


class OrderDatabase:
    def __init__(self, engine):
        self.engine = engine

    def transaction(self):
        return self.engine.begin()

