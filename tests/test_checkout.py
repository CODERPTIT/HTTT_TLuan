import pytest
from sqlalchemy import select, func
from data.infrastructure.order_database import orders, payments, shipments
from data.infrastructure.product_database import products


def add(services):
    return services.cart.addItem(services.cart.viewCart(1).cartId, 1, 2)


def test_empty_cart(services):
    with pytest.raises(ValueError, match="empty"):
        services.checkout.checkout(services.cart.viewCart(1).cartId, "123 Nguyen Hue", "0901234567")


@pytest.mark.parametrize("method,status", [("Cash on Delivery", "PENDING"), ("Simulated Card Payment", "PAID"), ("Simulated E-Wallet", "PAID")])
def test_successful_checkout(services, method, status):
    cart = add(services)
    services.checkout.service.payment_method = method
    order = services.checkout.checkout(cart.cartId, "123 Nguyen Hue", "0901234567")
    assert order.status == "CONFIRMED"
    assert order.items[0].quantity == 2
    assert services.cart.viewCart(1).isEmpty()
    assert services.order._getPayment(order.orderId).status == status
    assert services.order.trackOrder(order.orderId).status == "PREPARING"
    assert services.checkout.service.products.findById(1).quantityAvailable == 10
    assert any(item.interactionType == "PURCHASE" for item in services.recommendation.service.getInteractionHistory(1))


def test_payment_failure_releases_stock(services):
    cart = add(services)
    services.checkout.service.payment_method = "Simulated Card Payment"
    services.checkout.service.simulate_failure = True
    with pytest.raises(ValueError, match="payment failed"):
        services.checkout.checkout(cart.cartId, "123 Nguyen Hue", "0901234567")
    assert services.checkout.service.products.findById(1).quantityAvailable == 12
    assert services.cart.viewCart(1).items[0].quantity == 2
    assert services.order._listOrders(1) == []


def test_late_failure_rolls_back_everything(container, monkeypatch):
    with container.scope() as services:
        add(services)
    with pytest.raises(RuntimeError):
        with container.scope() as services:
            def fail(*args):
                raise RuntimeError("Shipment write failure")
            monkeypatch.setattr(services.checkout.service.shipments, "save", fail)
            services.checkout.checkout(services.cart.viewCart(1).cartId, "123 Nguyen Hue", "0901234567")
    with container.scope() as services:
        assert services.checkout.service.products.findById(1).quantityAvailable == 12
        assert len(services.cart.viewCart(1).items) == 1
        connection = services.checkout.service.orders.connection
        for table in (orders, payments, shipments):
            assert connection.execute(select(func.count()).select_from(table)).scalar() == 0


def test_stock_changed_before_checkout(services):
    cart = add(services)
    product = services.checkout.service.products.findById(1)
    product.quantityAvailable = 1
    services.checkout.service.products._updateStock(product)
    with pytest.raises(ValueError, match="Insufficient"):
        services.checkout.checkout(cart.cartId, "123 Nguyen Hue", "0901234567")


def test_order_price_snapshot(services):
    cart = add(services)
    order = services.checkout.checkout(cart.cartId, "123 Nguyen Hue", "0901234567")
    original = order.items[0].product.price
    services.checkout.service.orders.connection.execute(products.update().where(products.c.id == 1).values(price=1))
    assert services.order.viewOrder(order.orderId).items[0].product.price == original


def test_double_checkout_rejected(services):
    cart = add(services)
    services.checkout.checkout(cart.cartId, "123 Nguyen Hue", "0901234567")
    with pytest.raises(ValueError, match="empty"):
        services.checkout.checkout(cart.cartId, "123 Nguyen Hue", "0901234567")


def test_concurrent_checkout_cannot_oversell(container):
    from concurrent.futures import ThreadPoolExecutor
    with container.scope() as services:
        cart_ids = [services.cart.addItem(services.cart.viewCart(customerId).cartId, 1, 7).cartId
                    for customerId in (1, 2)]

    def checkout(cartId):
        try:
            with container.scope() as services:
                services.checkout.checkout(cartId, "123 Nguyen Hue", "0901234567")
            return "confirmed"
        except ValueError:
            return "unavailable"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(checkout, cart_ids))
    assert sorted(outcomes) == ["confirmed", "unavailable"]
    with container.scope() as services:
        assert services.checkout.service.products.findById(1).quantityAvailable == 5

