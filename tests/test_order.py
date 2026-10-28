import pytest


def test_order_and_tracking(services):
    cart = services.cart.addItem(services.cart.viewCart(1).cartId, 4, 1)
    order = services.checkout.checkout(cart.cartId, "123 Nguyen Hue", "0901234567")
    restored = services.order.viewOrder(order.orderId)
    assert restored.orderId == order.orderId
    assert restored.status == order.status
    assert restored.shippingAddress == order.shippingAddress
    assert restored.items[0].quantity == order.items[0].quantity
    assert restored.items[0].product.price == order.items[0].product.price
    assert services.order.trackOrder(order.orderId).trackingNumber.startswith("ABC-")
    services.order.service.updateStatus(order.orderId, "PROCESSING")
    assert services.order.viewOrder(order.orderId).status == "PROCESSING"


def test_missing_order(services):
    with pytest.raises(LookupError):
        services.order.viewOrder(999)
    with pytest.raises(LookupError):
        services.order.trackOrder(999)

