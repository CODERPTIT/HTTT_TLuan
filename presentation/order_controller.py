from application.commerce.order_service import OrderService
from domain.order.order import Order
from domain.order.shipment import Shipment
from domain.order.payment import Payment


class OrderController:
    def __init__(self, service: OrderService):
        self.service = service

    def viewOrder(self, orderId: int) -> Order:
        return self.service.getOrder(orderId)

    def trackOrder(self, orderId: int) -> Shipment:
        return self.service.getShipment(orderId)

    def _getPayment(self, orderId: int) -> Payment:
        return self.service._getPayment(orderId)

    def _listOrders(self, customerId: int) -> list[Order]:
        return self.service._listOrders(customerId)

