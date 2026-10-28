import re
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from uuid import uuid4
from domain.order.order import Order, OrderStatus
from domain.order.order_item import OrderItem
from domain.order.payment import Payment, PaymentStatus
from domain.order.shipment import Shipment, ShipmentStatus
from domain.interaction.interaction import InteractionType
from domain.cart.cart import Cart


class CheckoutService:
    METHODS = {"Cash on Delivery", "Simulated Card Payment", "Simulated E-Wallet"}

    def __init__(self, carts, products, orders, payments, shipments, interactions):
        self.carts = carts
        self.products = products
        self.orders = orders
        self.payments = payments
        self.shipments = shipments
        self.interactions = interactions
        self.payment_method = "Cash on Delivery"
        self.simulate_failure = False
        self.reserved = []

    def checkout(self, cartId: int, shippingAddress: str, recipientPhone: str) -> Order:
        if not 10 <= len(shippingAddress.strip()) <= 500:
            raise ValueError("Enter a shipping address between 10 and 500 characters")
        if not re.fullmatch(r"\+?[0-9][0-9 -]{7,18}", recipientPhone.strip()):
            raise ValueError("Enter a valid recipient phone number")
        if self.payment_method not in self.METHODS:
            raise ValueError("Choose a supported payment method")
        cart = self.carts.findById(cartId)
        self.validateCart(cart)
        self.validateAvailability(cart)
        self.reserved = []
        try:
            for item in cart.items:
                product = self.products.findById(item.product.productId)
                product.reserve(item.quantity)
                self.products._updateStock(product)
                self.reserved.append((item.product.productId, item.quantity))
            order = self.createOrder(cart, shippingAddress.strip(), recipientPhone.strip())
            payment = self.processPayment(order)
            if payment.status == PaymentStatus.FAILED:
                raise ValueError("Simulated payment failed. Your cart and stock are unchanged.")
            self.confirmOrder(order)
            self.orders.save(order)
            payment._orderId = order.orderId
            self.payments.save(payment)
            shipment = Shipment("ABC-" + uuid4().hex[:12].upper(), ShipmentStatus.PREPARING,
                "ABC Demo Delivery", datetime.now(timezone.utc) + timedelta(days=3))
            shipment._orderId = order.orderId
            self.shipments.save(shipment)
            for item in cart.items:
                self.interactions._record(cart.customerId, item.product, InteractionType.PURCHASE)
            cart.items.clear()
            self.carts.update(cart)
            self.reserved = []
            return order
        except Exception:
            self.releaseReservedStock(cart)
            raise

    def validateCart(self, cart: Cart) -> bool:
        if cart.isEmpty():
            raise ValueError("Your cart is empty")
        if any(type(item.quantity) is not int or item.quantity <= 0 for item in cart.items):
            raise ValueError("Invalid cart quantity")
        return True

    def validateAvailability(self, cart: Cart) -> bool:
        for item in cart.items:
            product = self.products.findById(item.product.productId)
            if product.status != "ACTIVE" or not product.isAvailable(item.quantity):
                raise ValueError("Insufficient stock for " + item.product.productName)
        return True

    def calculateTotal(self, cart: Cart) -> Decimal:
        return cart.calculateTotal()

    def createOrder(self, cart: Cart, shippingAddress: str, recipientPhone: str) -> Order:
        return Order(0, shippingAddress, recipientPhone, cart.customerId,
                     items=[OrderItem(0, item.quantity, item.product) for item in cart.items])

    def processPayment(self, order: Order) -> Payment:
        failed = self.simulate_failure and self.payment_method != "Cash on Delivery"
        status = PaymentStatus.FAILED if failed else PaymentStatus.PENDING if self.payment_method == "Cash on Delivery" else PaymentStatus.PAID
        return Payment(0, self.payment_method, sum((item.product.price * item.quantity for item in order.items), Decimal(0)),
                       status, "DEMO-" + uuid4().hex[:16], datetime.now(timezone.utc) if status == PaymentStatus.PAID else None)

    def confirmOrder(self, order: Order) -> None:
        order.updateStatus(OrderStatus.CONFIRMED)

    def releaseReservedStock(self, cart: Cart) -> None:
        for productId, quantity in self.reserved:
            product = self.products.findById(productId)
            product.release(quantity)
            self.products._updateStock(product)
        self.reserved = []

