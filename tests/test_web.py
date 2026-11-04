import re
import pytest


@pytest.mark.parametrize("url", ["/", "/search", "/search?q=gaming+laptop", "/search?q=nonsensexyz",
    "/search?q=phone&brand=Samsung&color=blue&available=true&sort=price_asc", "/products/1", "/cart", "/checkout",
    "/orders", "/profile", "/api/recommendations?productId=1"])
def test_main_routes(client, url):
    response = client.get(url)
    assert response.status_code == 200
    assert "Traceback" not in response.text


def test_browse_catalog_does_not_claim_a_match_score(client):
    response = client.get("/search?q=electronics")
    assert response.status_code == 200
    assert "ASUS ROG Strix G16" in response.text
    assert "product-match-badge" not in response.text


def test_category_navigation_uses_catalog_filter_without_semantic_search(client, monkeypatch):
    from application.search.search_service import SearchService

    def unexpected_semantic_search(*args, **kwargs):
        raise AssertionError("Category navigation must not call semantic search")

    monkeypatch.setattr(SearchService, "search", unexpected_semantic_search)
    home = client.get("/")
    assert "/search?q=electronics&amp;category=Laptops" in home.text

    response = client.get("/search", params={"q": "electronics", "category": "Laptops"})
    assert response.status_code == 200
    assert "ASUS ROG Strix G16" in response.text
    assert "Samsung Galaxy S24" not in response.text


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
    orders_page = client.get("/orders")
    assert "ASUS ROG Strix G16" in orders_page.text
    assert "32,990,000" in orders_page.text
    assert "Track order" in orders_page.text
    for url in ["/orders/1", "/orders/1/tracking", "/orders/1/success"]:
        assert client.get(url).status_code == 200
    assert "Your cart is empty" in client.get("/cart").text


def test_multimodal_routes(client):
    search_page = client.get("/")
    assert 'id="image-voice-record"' in search_page.text
    assert 'id="image-voice-status"' in search_page.text
    response = client.post("/search/voice", data={"transcript": "wireless headphones"})
    assert response.status_code == 200
    assert "Voice search" in response.text
    image = client.get("/media/product-4.png")
    response = client.post("/search/image", files={"image": ("photo.png", image.content, "image/png")})
    assert response.status_code == 200
    assert "Image search" in response.text
    response = client.post("/search/image", data={"q": "Samsung phone", "crop_box": "[0.1,0.1,0.9,0.9]"},
                           files={"image": ("photo.png", image.content, "image/png")})
    assert response.status_code == 200
    assert "Image + text search" in response.text
    detected = client.post("/search/detect", files={"image": ("photo.png", image.content, "image/png")})
    assert detected.json() == {"available": False, "objects": []}


def test_audio_transcription_route(client, monkeypatch):
    from types import SimpleNamespace
    import openai
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    transcription = SimpleNamespace(create=lambda **kwargs: SimpleNamespace(text="Samsung phone"))
    monkeypatch.setattr(openai, "OpenAI", lambda **kwargs: SimpleNamespace(
        audio=SimpleNamespace(transcriptions=transcription)))
    response = client.post("/search/transcribe", files={"audio": ("recording.webm", b"recorded audio", "audio/webm")},
                           headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert response.json() == {"transcript": "Samsung phone"}


def test_errors(client):
    assert client.get("/products/999").status_code == 404
    assert client.get("/orders/999").status_code == 404
    assert client.post("/cart/items", data={"productId": 24, "quantity": 1}).status_code == 400
    assert client.post("/cart/items", data={"productId": 1, "quantity": 0}).status_code == 422
    assert client.patch("/cart/items/1", json={"quantity": 1.5}).status_code == 422
    assert client.post("/search/image", files={"image": ("fake.png", b"bad", "image/png")}).status_code == 400
    assert client.post("/search/image", data={"crop_box": "[0,0,2,1]"},
                       files={"image": ("photo.png", client.get("/media/product-4.png").content,
                                        "image/png")}).status_code == 400
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

