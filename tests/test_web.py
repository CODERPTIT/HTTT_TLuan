import re
import pytest


@pytest.mark.parametrize("url", ["/", "/search", "/search?q=gaming+laptop", "/search?q=nonsensexyz",
    "/search?q=phone&brand=Samsung&available=true&sort=price_asc", "/products/1", "/cart", "/checkout",
    "/orders", "/api/recommendations?customerId=1&productId=1"])
def test_main_routes(client, url):
    response = client.get(url)
    assert response.status_code == 200
    assert "Traceback" not in response.text


def test_complete_browser_flow(client):
    response = client.post("/cart/items", data={"productId": 1, "quantity": 2}, headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert client.patch("/cart/items/1", json={"quantity": 1}).status_code == 200
    assert "ASUS ROG" in client.get("/checkout").text
    response = client.post("/checkout", data={"shippingAddress": "123 Nguyen Hue", "recipientPhone": "0901234567",
        "paymentMethod": "Simulated Card Payment"})
    assert response.status_code == 200
    assert "Order confirmed" in response.text
    assert "PAID" in response.text
    for url in ["/orders/1", "/orders/1/tracking", "/orders/1/success"]:
        assert client.get(url).status_code == 200
    assert "Your cart is empty" in client.get("/cart").text


def test_multimodal_routes(client):
    response = client.post("/search/voice", data={"transcript": "wireless headphones"})
    assert response.status_code == 200
    assert "Voice search" in response.text
    image = client.get("/media/product-4.png")
    response = client.post("/search/image", files={"image": ("photo.png", image.content, "image/png")})
    assert response.status_code == 200
    assert "Image search" in response.text


def test_errors(client):
    assert client.get("/products/999").status_code == 404
    assert client.get("/orders/999").status_code == 404
    assert client.post("/cart/items", data={"productId": 24, "quantity": 1}).status_code == 400
    assert client.post("/cart/items", data={"productId": 1, "quantity": 0}).status_code == 422
    assert client.patch("/cart/items/1", json={"quantity": 1.5}).status_code == 422
    assert client.post("/search/image", files={"image": ("fake.png", b"bad", "image/png")}).status_code == 400
    assert client.get("/search?image=../electronics.db").status_code == 400
    assert client.post("/checkout", data={"shippingAddress": "x", "recipientPhone": "x"}).status_code == 400


def test_assets_and_html_escaping(client):
    response = client.get("/")
    assets = re.findall(r'(?:src|href)="(/(?:static|media)/[^"]+)"', response.text)
    assert assets
    for asset in assets:
        assert client.get(asset).status_code == 200
    response = client.get("/search", params={"q": "<script>alert(1)</script>"})
    assert "<script>alert(1)</script>" not in response.text

