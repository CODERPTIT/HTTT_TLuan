from application.commerce.checkout_service import CheckoutService
from domain.order.order import Order


class CheckoutController:
    def __init__(self, service: CheckoutService):
        self.service = service

    def checkout(self, cartId: int, shippingAddress: str, recipientPhone: str) -> Order:
        return self.service.checkout(cartId, shippingAddress, recipientPhone)

