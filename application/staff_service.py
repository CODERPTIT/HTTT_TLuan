from decimal import Decimal


class StaffService:
    def __init__(self, staff):
        self.staff = staff

    def products(self):
        return self.staff.products()

    def orders(self):
        return self.staff.orders()

    def updateProduct(self, productId: int, price: Decimal, status: str) -> None:
        self.staff.update_product(productId, price, status)

    def updateStock(self, productId: int, quantity: int) -> None:
        self.staff.update_stock(productId, quantity)

    def processOrder(self, orderId: int) -> None:
        self.staff.process_order(orderId)

    def shipOrder(self, orderId: int) -> None:
        self.staff.ship_order(orderId)

    def report(self):
        return self.staff.report()
