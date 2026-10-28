import pytest


def test_cart_operations(services):
    cart = services.cart.viewCart(1)
    cart = services.cart.addItem(cart.cartId, 1, 2)
    cart = services.cart.addItem(cart.cartId, 1, 1)
    assert cart.items[0].quantity == 3
    assert cart.calculateTotal() == cart.items[0].product.price * 3
    cart = services.cart.updateQuantity(cart.cartId, 1, 1)
    assert cart.items[0].quantity == 1
    cart = services.cart.removeItem(cart.cartId, 1)
    assert cart.isEmpty()


@pytest.mark.parametrize("quantity", [0, -1, 1.5, True, 999])
def test_invalid_quantity(services, quantity):
    with pytest.raises(ValueError):
        services.cart.addItem(services.cart.viewCart(1).cartId, 1, quantity)


def test_product_stock(services):
    product = services.cart.service.products.findById(1)
    product.quantityAvailable = 3
    assert product.isAvailable(3)
    assert not product.isAvailable(0)
    product.reserve(2)
    assert product.quantityAvailable == 1
    with pytest.raises(ValueError):
        product.reserve(2)
    product.release(2)
    product.reserve(1)
    product.release(4)
    assert product.quantityAvailable == 6


def test_persistence(container):
    with container.scope() as services:
        services.cart.addItem(services.cart.viewCart(1).cartId, 2, 2)
    with container.scope() as services:
        assert services.cart.viewCart(1).items[0].quantity == 2


def test_product_specifications_and_serials_persist(services):
    repository = services.cart.service.products
    product = repository.findById(1)
    product.specifications[0].specValue = "32 GB RAM"
    product.quantityAvailable = 8
    repository.update(product)
    restored = repository.findById(1)
    assert restored.specifications[0].specValue == "32 GB RAM"
    assert restored.quantityAvailable == 8
    assert restored.units[0].serialNumber == "ABC-001-001"


def test_stock_schema_has_no_inventory_table(container):
    from sqlalchemy import inspect
    schema = inspect(container.database.engine)
    assert "inventories" not in schema.get_table_names()
    assert "quantity_available" in {column["name"] for column in schema.get_columns("products")}
    assert "product_id" in {column["name"] for column in schema.get_columns("product_units")}

