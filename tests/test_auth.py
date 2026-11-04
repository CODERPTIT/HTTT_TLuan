import sqlite3

from sqlalchemy import inspect, select

from bootstrap import Bootstrap
from data.repository.account_repository import hash_password
from data.infrastructure.order_database import (users, customers, staff, shipping_providers, shipments,
                                                payments, orders, interactions, search_queries)
from data.infrastructure.product_database import products


def sign_in(client, email, password):
    return client.post("/login", data={"email": email, "password": password})


def test_customer_authentication_and_data_isolation(client):
    assert client.post("/logout").status_code == 200
    login_page = client.get("/login")
    assert "Shipping Provider" in login_page.text
    assert "shipping@abc.test" in login_page.text
    assert client.get("/profile", follow_redirects=False).headers["location"].startswith("/login")
    with client.app.state.container.database.engine.connect() as connection:
        search_count = connection.execute(select(search_queries.c.id)).all()
        interaction_count = connection.execute(select(interactions.c.id)).all()
    assert client.get("/").status_code == 200
    assert client.get("/search?q=gaming+laptop").status_code == 200
    product_page = client.get("/products/1")
    assert product_page.status_code == 200
    assert "Sign in to buy" in product_page.text
    assert client.get("/api/recommendations").status_code == 200
    image = client.get("/media/product-4.png")
    assert client.post("/search/detect", files={"image": ("phone.png", image.content, "image/png")}).status_code == 200
    assert client.post("/search/image", files={"image": ("phone.png", image.content, "image/png")},
                       follow_redirects=False).status_code == 303
    assert client.post("/search/voice", data={"transcript": "wireless headphones"},
                       follow_redirects=False).status_code == 303
    with client.app.state.container.database.engine.connect() as connection:
        assert len(connection.execute(select(search_queries.c.id)).all()) == len(search_count)
        assert len(connection.execute(select(interactions.c.id)).all()) == len(interaction_count)
    assert client.get("/cart", follow_redirects=False).headers["location"].startswith("/login")
    assert client.post("/cart/items", data={"productId": 1, "quantity": 1},
                       headers={"Accept": "application/json"}).status_code == 401
    purchase_redirect = client.post("/cart/items", data={"productId": 1, "quantity": 1},
                                    follow_redirects=False)
    assert purchase_redirect.status_code == 303
    assert purchase_redirect.headers["location"] == "/login?next=/cart"
    client.cookies.set("abc_session", "tampered")
    assert client.get("/cart", follow_redirects=False).status_code == 303
    client.cookies.delete("abc_session")
    assert sign_in(client, "demo1@example.test", "wrong-password").status_code == 401
    assert sign_in(client, "demo1@example.test", "DemoCustomer123!").status_code == 200
    profile = client.get("/profile")
    assert profile.status_code == 200
    assert "Demo Customer 1" in profile.text
    assert "demo1@example.test" in profile.text
    assert "Customer" in profile.text
    assert client.post("/profile", data={"name": "Demo Customer One", "phone": "0912345678",
        "address": "456 Le Loi, Ho Chi Minh City"}, follow_redirects=False).status_code == 303
    updated_profile = client.get("/profile")
    assert "Demo Customer One" in updated_profile.text
    assert "0912345678" in updated_profile.text
    client.post("/cart/items", data={"productId": 1, "quantity": 1})
    checkout_page = client.get("/checkout")
    assert "Demo Customer One" in checkout_page.text
    assert "456 Le Loi, Ho Chi Minh City" in checkout_page.text
    client.post("/checkout", data={"shippingAddress": "123 Nguyen Hue", "recipientPhone": "0901234567"})
    client.post("/logout")
    assert sign_in(client, "demo2@example.test", "DemoCustomer123!").status_code == 200
    second_profile = client.get("/profile")
    assert "Demo Customer 2" in second_profile.text
    assert "Demo Customer One" not in second_profile.text
    assert "Your cart is empty" in client.get("/cart").text
    assert "ASUS ROG Strix G16" not in client.get("/orders").text
    for path in ("/orders/1", "/orders/1/tracking", "/orders/1/success"):
        assert client.get(path, follow_redirects=False).status_code == 404
    assert client.get("/api/recommendations", params={"customerId": 1, "productId": 1}).status_code == 200
    assert client.get("/staff", follow_redirects=False).status_code == 403


def test_registration_and_staff_workflows(client):
    client.post("/logout")
    assert client.post("/register", data={"name": "New Buyer", "email": "buyer@example.test",
        "password": "SecurePass123!"}).status_code == 200
    client.post("/cart/items", data={"productId": 1, "quantity": 1})
    assert "New Buyer" in client.get("/checkout").text
    assert client.post("/checkout", data={"shippingAddress": "123 Nguyen Hue", "recipientPhone": "0901234567"}).status_code == 200
    with client.app.state.container.database.engine.connect() as connection:
        buyer = connection.execute(select(users).where(users.c.email == "buyer@example.test")).mappings().one()
        assert buyer["role"] == "CUSTOMER"
        assert buyer["password_hash"] != "SecurePass123!"
        assert connection.execute(select(customers.c.id).where(customers.c.id == buyer["id"])).scalar_one()
        assert connection.execute(select(staff.c.id).join(users).where(
            users.c.email == "admin@abc.test")).scalar_one()
    client.post("/logout")
    assert sign_in(client, "admin@abc.test", "DemoStaff123!").status_code == 200
    admin_profile = client.get("/profile")
    assert admin_profile.status_code == 200
    assert "admin@abc.test" in admin_profile.text
    assert "Administrator" in admin_profile.text
    assert client.post("/profile", data={"name": "Changed", "phone": "", "address": ""},
                       follow_redirects=False).status_code == 403
    assert "Product catalogue" in client.get("/staff").text
    assert client.get("/cart", follow_redirects=False).status_code == 403
    assert client.post("/staff/products/1", data={"price": "29990000", "status": "ACTIVE"}).status_code == 200
    client.post("/logout")
    assert sign_in(client, "sales@abc.test", "DemoStaff123!").status_code == 200
    assert "Order #1" in client.get("/staff").text
    assert client.post("/staff/orders/1/process").status_code == 200
    client.post("/logout")
    assert sign_in(client, "warehouse@abc.test", "DemoStaff123!").status_code == 200
    assert client.post("/staff/products/1", data={"price": "1", "status": "ACTIVE"},
        follow_redirects=False).status_code == 403
    assert client.post("/staff/stock/1", data={"quantity": "7"}).status_code == 200
    assert client.post("/staff/orders/1/ship").status_code == 200
    with client.app.state.container.database.engine.connect() as connection:
        row = connection.execute(select(products.c.price, products.c.quantity_available).where(products.c.id == 1)).one()
        assert row.price == 29990000 and row.quantity_available == 7
        assert connection.execute(select(orders.c.status).where(orders.c.id == 1)).scalar_one() == "SHIPPED"
    client.post("/logout")
    assert sign_in(client, "shipping@abc.test", "DemoShipping123!").status_code == 200
    provider_profile = client.get("/profile")
    assert "ABC-DELIVERY" in provider_profile.text
    assert client.get("/staff", follow_redirects=False).status_code == 403
    delivery_dashboard = client.get("/shipping")
    assert delivery_dashboard.status_code == 200
    assert "Out for delivery" in delivery_dashboard.text
    assert client.post("/shipping/orders/1/out-for-delivery").status_code == 200
    assert "Mark delivered" in client.get("/shipping").text
    assert client.post("/shipping/orders/1/deliver").status_code == 200
    with client.app.state.container.database.engine.connect() as connection:
        provider_id = connection.execute(select(shipping_providers.c.id).join(users,
            shipping_providers.c.user_id == users.c.id).where(
                users.c.email == "shipping@abc.test")).scalar_one()
        shipment = connection.execute(select(shipments).where(shipments.c.order_id == 1)).mappings().one()
        assert shipment["shipping_provider_id"] == provider_id
        assert shipment["status"] == "DELIVERED" and shipment["delivered"]
        assert connection.execute(select(orders.c.status).where(orders.c.id == 1)).scalar_one() == "DELIVERED"
        assert connection.execute(select(payments.c.status).where(payments.c.order_id == 1)).scalar_one() == "PAID"
    client.post("/logout")
    assert sign_in(client, "manager@abc.test", "DemoStaff123!").status_code == 200
    assert "Paid revenue" in client.get("/staff").text
    assert client.post("/staff/stock/1", data={"quantity": "2"}, follow_redirects=False).status_code == 403
    client.post("/logout")
    sign_in(client, "demo1@example.test", "DemoCustomer123!")
    assert client.post("/cart/items", data={"productId": 1, "quantity": 1},
        headers={"Origin": "https://other.example"}, follow_redirects=False).status_code == 403


def test_legacy_accounts_are_migrated_to_user_inheritance(tmp_path):
    database_path = tmp_path / "electronics.db"
    connection = sqlite3.connect(database_path)
    connection.executescript("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY, name VARCHAR, email VARCHAR, phone VARCHAR, address TEXT
        );
        CREATE TABLE accounts (
            id INTEGER PRIMARY KEY, email VARCHAR NOT NULL UNIQUE, password_hash VARCHAR NOT NULL,
            role VARCHAR NOT NULL, customer_id INTEGER UNIQUE REFERENCES customers(id),
            active INTEGER NOT NULL DEFAULT 1
        );
    """)
    password_hash = hash_password("LegacyPass123!")
    connection.execute("INSERT INTO customers VALUES (10, ?, ?, ?, ?)",
        ("Legacy Buyer", "legacy@example.test", "0911222333", "Legacy address"))
    connection.execute("INSERT INTO accounts VALUES (1, ?, ?, 'CUSTOMER', 10, 1)",
        ("legacy@example.test", password_hash))
    connection.execute("INSERT INTO accounts VALUES (2, ?, ?, 'MANAGER', NULL, 1)",
        ("legacy.manager@example.test", password_hash))
    connection.commit()
    connection.close()

    container = Bootstrap(tmp_path)
    try:
        assert "accounts" not in inspect(container.database.engine).get_table_names()
        with container.database.engine.connect() as migrated:
            customer_user = migrated.execute(select(users).where(
                users.c.email == "legacy@example.test")).mappings().one()
            assert customer_user["id"] == 10
            assert customer_user["full_name"] == "Legacy Buyer"
            assert migrated.execute(select(customers.c.delivery_address).where(
                customers.c.id == 10)).scalar_one() == "Legacy address"
            manager = migrated.execute(select(users).where(
                users.c.email == "legacy.manager@example.test")).mappings().one()
            assert migrated.execute(select(staff.c.department).where(
                staff.c.id == manager["id"])).scalar_one() == "Management"
        with container.scope() as services:
            assert services.auth.authenticate("legacy@example.test", "LegacyPass123!")
    finally:
        container.database.engine.dispose()
