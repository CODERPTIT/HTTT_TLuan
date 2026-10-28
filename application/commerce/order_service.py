from domain.order.order import Order, OrderStatus
from domain.order.shipment import Shipment
from domain.order.payment import Payment


class OrderService:
    def __init__(self, orders, shipments, payments):
        self.orders = orders
        self.shipments = shipments
        self.payments = payments

    def getOrder(self, orderId: int) -> Order:
        return self.orders.findById(orderId)

    def updateStatus(self, orderId: int, status: OrderStatus) -> None:
        order = self.getOrder(orderId)
        order.updateStatus(status)
        self.orders.update(order)

    def getShipment(self, orderId: int) -> Shipment:
        self.getOrder(orderId)
        return self.shipments.findByOrder(orderId)

    def _getPayment(self, orderId: int) -> Payment:
        return self.payments.findByOrder(orderId)

    def _listOrders(self, customerId: int) -> list[Order]:
        return self.orders.findByCustomer(customerId)

