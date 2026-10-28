from datetime import datetime
from sqlalchemy import select, delete
from domain.cart.cart import Cart
from domain.cart.cart_item import CartItem
from data.infrastructure.order_database import carts, cart_items


class CartRepository:
    def __init__(self, connection, products):
        self.connection = connection
        self.products = products

    def findById(self, cartId: int) -> Cart:
        row = self.connection.execute(select(carts).where(carts.c.id == cartId)).mappings().first()
        if row is None:
            raise LookupError("Cart not found")
        items = self.connection.execute(select(cart_items).where(cart_items.c.cart_id == cartId)).mappings()
        return Cart(row["id"], row["customer_id"], datetime.fromisoformat(row["created_at"]),
                    [CartItem(item["id"], item["quantity"], self.products.findById(item["product_id"])) for item in items])

    def findByCustomer(self, customerId: int) -> Cart:
        identity = self.connection.execute(select(carts.c.id).where(carts.c.customer_id == customerId)).scalar()
        if identity is None:
            cart = Cart(0, customerId)
            self.save(cart)
            return cart
        return self.findById(identity)

    def save(self, cart: Cart) -> None:
        cart.cartId = self.connection.execute(carts.insert().values(customer_id=cart.customerId,
            created_at=cart.createdAt.isoformat())).inserted_primary_key[0]
        self.update(cart)

    def update(self, cart: Cart) -> None:
        self.connection.execute(delete(cart_items).where(cart_items.c.cart_id == cart.cartId))
        for item in cart.items:
            item.cartItemId = self.connection.execute(cart_items.insert().values(cart_id=cart.cartId,
                product_id=item.product.productId, quantity=item.quantity)).inserted_primary_key[0]

