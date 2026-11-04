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
    assert services.search.text("RTX 4060")[0].product.productId == 1
    assert services.search.text("nonsensexyz") == []
    saved = services.search.service.searches.findById(query.searchQueryId)
    assert isinstance(saved, TextQuery)
    assert saved.queryText == "gaming laptop"
    assert services.search.service.searches.findResults(query.searchQueryId) == results


@pytest.mark.parametrize("query", ["smartphone", "SMARTPHONE", "phone", "phones"])
def test_smartphone_aliases_find_products(services, query):
    results = services.search.text(query)
    assert results
    assert all(result.product.category.categoryName == "Smartphones" for result in results)


@pytest.mark.parametrize("query,product_ids", [
    ("chuột", {22}), ("chuot", {22}), ("chuột không dây", {22}),
    ("điện thoại", {4, 5, 6}), ("tai nghe", {10}), ("màn hình", {24}),
])
def test_vietnamese_product_terms(services, query, product_ids):
    results = services.search.text(query)
    assert results
    assert results[0].product.productId in product_ids


def test_semantic_search_does_not_require_shared_keywords(services):
    class SemanticEmbedding:
        backend = "openai"

        @staticmethod
        def tokens(text):
            return text.lower().split()

        def embedMany(self, texts):
            return [[1.0, 0.0] if index == 0 or "WH-1000XM5" in text else [0.0, 1.0]
                    for index, text in enumerate(texts)]

    services.search.service.ranking.text = SemanticEmbedding()
    results = services.search.text("quiet commute")
    assert results[0].product.productName == "Sony WH-1000XM5"


def test_voice_transcript(services):
    direct = services.search.text("wireless noise cancelling headphones")
    voice = services.search.search(VoiceQuery(transcribedText="wireless noise cancelling headphones"))
    fallback = services.search.search(VoiceQuery(audioReference="transcript:wireless noise cancelling headphones"))
    assert direct == voice == fallback
    assert voice[0].product.productId == 10


def test_image_deterministic(services, container):
    content = (container.images.root / "product-4.png").read_bytes()
    reference, first = services.search.image(content, "phone.png", "image/png")
    second = services.search.search(ImageQuery(imageReference=reference))
    assert first == second
    assert first[0].product.productId == 4
    assert first[0].relevanceScore == Decimal("1.0")


def test_absolute_threshold_skips_low_scoring_queries(services):
    class UnrelatedText:
        @staticmethod
        def tokens(text):
            return text.lower().split()

        @staticmethod
        def embedMany(texts):
            return [[1.0, 0.0]] + [[0.0, 1.0] for _ in texts[1:]]

    ranking = services.search.service.ranking
    ranking.text = UnrelatedText()
    ranking.reranker.rerank = lambda query, candidates: (_ for _ in ()).throw(
        AssertionError("Reranker should not receive low-scoring candidates"))
    assert services.search.text("completely unrelated") == []

    class UnrelatedImage:
        @staticmethod
        def embedMany(references):
            return [[1.0, 0.0]] + [[0.0, 1.0] for _ in references[1:]]

    ranking.image = UnrelatedImage()
    assert services.search.search(ImageQuery(imageReference="product-4.png")) == []


def test_image_text_and_object_crop_are_saved(services, container):
    content = (container.images.root / "product-4.png").read_bytes()
    reference, results = services.search.image(content, "phone.png", "image/png",
                                                "Samsung phone", [0.1, 0.1, 0.9, 0.9])
    assert reference.endswith(".jpg")
    assert results
    from PIL import Image
    with Image.open(container.images.root / "product-4.png") as original, Image.open(container.images.root / reference) as cropped:
        assert cropped.width < original.width
        assert cropped.height < original.height
    saved = services.search.service.searches.findByCustomer(1)[0]
    assert isinstance(saved, ImageQuery)
    assert saved.queryText == "samsung phone"
    assert saved.imageReference == reference
    assert services.search.service.searches.findResults(saved.searchQueryId) == results


def test_image_text_changes_ranking(services):
    class EqualImages:
        backend = "basic"

        @staticmethod
        def embedMany(references):
            return [[1.0, 0.0] for _ in references]

    services.search.service.ranking.image = EqualImages()
    visual = services.search.search(ImageQuery(imageReference="product-4.png"))
    combined = services.search.search(ImageQuery(imageReference="product-4.png", queryText="Samsung"))
    assert visual[0].product.productId == 1
    assert combined[0].product.brand == "Samsung"


def test_image_text_budget_excludes_expensive_products(services):
    results = services.search.search(ImageQuery(imageReference="product-4.png",
                                                queryText="phone under 20 million"))
    assert results
    assert all(result.product.price <= 20000000 for result in results)


def test_upload_content_must_match_declared_type(services, container):
    content = (container.images.root / "product-4.png").read_bytes()
    with pytest.raises(ValueError):
        services.search.image(content, "phone.jpg", "image/jpeg")


def test_budget_and_filters(services):
    results = services.search.text("phone under 20 million")
    assert results
    assert all(result.product.price <= 20000000 for result in results)
    filtered = services.search.filterResults(results, brand="Samsung", sort="price_asc")
    assert all(result.product.brand == "Samsung" for result in filtered)
    assert filtered[0].product.price <= filtered[-1].product.price
    blue = services.search.filterResults(results, color="blue")
    assert all(any(spec.specName == "Color" and spec.specValue == "blue"
                   for spec in result.product.specifications) for result in blue)


@pytest.mark.parametrize("query,minimum,maximum", [
    ("đồ dưới 3 triệu", 0, 3000000),
    ("products under 5000k", 0, 5000000),
    ("đồ từ 2 triệu đến 3 triệu", 2000000, 3000000),
    ("products from 5 million to 20 million", 5000000, 20000000),
])
def test_natural_language_price_filters(services, query, minimum, maximum):
    results = services.search.text(query)
    assert results
    assert all(minimum <= result.product.price <= maximum for result in results)


def test_combined_brand_category_color_and_price_filters(services):
    results = services.search.text("điện thoại Samsung màu xanh dưới 10 triệu")
    assert [result.product.productId for result in results] == [6]
    product = results[0].product
    assert product.brand == "Samsung"
    assert product.category.categoryName == "Smartphones"
    assert product.price <= 10000000
    assert any(spec.specName == "Color" and spec.specValue == "blue" for spec in product.specifications)


def test_vietnamese_color_filter_matches_catalog_metadata(services):
    results = services.search.text("tìm cho tôi smartphone màu đen")
    assert [result.product.productId for result in results] == [4]
    assert all(any(spec.specName == "Color" and spec.specValue == "black"
                   for spec in result.product.specifications) for result in results)


def test_filter_with_no_matching_products_skips_reranker(services):
    reranker = services.search.service.ranking.reranker
    reranker.rerank = lambda query, candidates: (_ for _ in ()).throw(
        AssertionError("Reranker should not run without filter matches"))
    assert services.search.text("đồ dưới 1 triệu") == []


def test_availability_filter_excludes_out_of_stock_product(services):
    results = services.search.text("monitor còn hàng")
    assert all(result.product.quantityAvailable > 0 for result in results)
    assert all(result.product.productId != 24 for result in results)


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
        services.search.image(content, filename, mime)

