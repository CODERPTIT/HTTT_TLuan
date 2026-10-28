from domain.interaction.interaction import InteractionType
from domain.cart.cart import Cart
from domain.product.product import Product


class CartService:
    def __init__(self, carts, products, interactions):
        self.carts = carts
        self.products = products
        self.interactions = interactions

    def getCart(self, customerId: int) -> Cart:
        return self.carts.findByCustomer(customerId)

    def _validate(self, product: Product, quantity: int) -> None:
        if product.status != "ACTIVE" or not product.isAvailable(quantity):
            raise ValueError("Product unavailable or insufficient stock")

    def addItem(self, cartId: int, productId: int, quantity: int) -> Cart:
        cart = self.carts.findById(cartId)
        product = self.products.findById(productId)
        existing = cart.findItem(product)
        if type(quantity) is not int or quantity <= 0:
            raise ValueError("Quantity must be a positive integer")
        self._validate(product, quantity + (existing.quantity if existing else 0))
        cart.addItem(product, quantity)
        self.carts.update(cart)
        self.interactions._record(cart.customerId, product, InteractionType.ADD_TO_CART)
        return cart

    def updateQuantity(self, cartId: int, productId: int, quantity: int) -> Cart:
        cart = self.carts.findById(cartId)
        product = self.products.findById(productId)
        self._validate(product, quantity)
        cart.updateQuantity(product, quantity)
        self.carts.update(cart)
        return cart

    def removeItem(self, cartId: int, productId: int) -> Cart:
        cart = self.carts.findById(cartId)
        cart.removeItem(self.products.findById(productId))
        self.carts.update(cart)
        return cart

