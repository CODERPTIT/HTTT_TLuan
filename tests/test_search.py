from decimal import Decimal
from domain.search.text_query import TextQuery
from domain.search.voice_query import VoiceQuery
from domain.search.image_query import ImageQuery
import pytest


def test_text_ranking_and_specification(services):
    query = TextQuery(queryText="gaming laptop")
    results = services.search.search(query)
    assert results[0].product.productId == 1
    assert [item.rank for item in results] == list(range(1, len(results) + 1))
    assert all(isinstance(item.relevanceScore, Decimal) for item in results)
    assert services.search._text("RTX 4060")[0].product.productId == 1
    assert services.search._text("nonsensexyz") == []
    saved = services.search.service.searches.findById(query.searchQueryId)
    assert isinstance(saved, TextQuery)
    assert saved.queryText == "gaming laptop"
    assert services.search.service.searches.findResults(query.searchQueryId) == results


def test_voice_transcript(services):
    direct = services.search._text("wireless noise cancelling headphones")
    voice = services.search.search(VoiceQuery(transcribedText="wireless noise cancelling headphones"))
    fallback = services.search.search(VoiceQuery(audioReference="transcript:wireless noise cancelling headphones"))
    assert direct == voice == fallback
    assert voice[0].product.productId == 10


def test_image_deterministic(services, container):
    content = (container.images.root / "product-4.png").read_bytes()
    reference, first = services.search._image(content, "phone.png", "image/png")
    second = services.search.search(ImageQuery(imageReference=reference))
    assert first == second
    assert first[0].product.productId == 4


def test_upload_content_must_match_declared_type(services, container):
    content = (container.images.root / "product-4.png").read_bytes()
    with pytest.raises(ValueError):
        services.search._image(content, "phone.jpg", "image/jpeg")


def test_budget_and_filters(services):
    results = services.search._text("phone under 20 million")
    assert results
    assert all(result.product.price <= 20000000 for result in results)
    filtered = services.search._filterResults(results, brand="Samsung", sort="price_asc")
    assert all(result.product.brand == "Samsung" for result in filtered)
    assert filtered[0].product.price <= filtered[-1].product.price


@pytest.mark.parametrize("reference", ["../electronics.db", "C:/Windows/win.ini", "..\\electronics.db"])
def test_image_path_rejected(services, reference):
    with pytest.raises(ValueError):
        services.search.search(ImageQuery(imageReference=reference))


@pytest.mark.parametrize("filename,mime,content", [
    ("test.png", "image/png", b"not an image"),
    ("test.exe", "image/png", b"x"),
    ("test.jpg", "image/gif", b"x"),
    ("test.png", "image/png", b"x" * (5 * 1024 * 1024 + 1)),
], ids=["corrupt", "extension", "mime", "oversized"])
def test_invalid_upload(services, filename, mime, content):
    with pytest.raises(ValueError):
        services.search._image(content, filename, mime)

