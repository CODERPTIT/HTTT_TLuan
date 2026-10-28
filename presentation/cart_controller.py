from application.commerce.cart_service import CartService
from domain.cart.cart import Cart


class CartController:
    def __init__(self, service: CartService):
        self.service = service

    def viewCart(self, customerId: int) -> Cart:
        return self.service.getCart(customerId)

    def addItem(self, cartId: int, productId: int, quantity: int) -> Cart:
        return self.service.addItem(cartId, productId, quantity)

    def updateQuantity(self, cartId: int, productId: int, quantity: int) -> Cart:
        return self.service.updateQuantity(cartId, productId, quantity)

    def removeItem(self, cartId: int, productId: int) -> Cart:
        return self.service.removeItem(cartId, productId)

