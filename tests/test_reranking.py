import json
from decimal import Decimal
from math import sqrt
from types import SimpleNamespace

import pytest

from application.search.reranking_service import RerankingService
from domain.search.image_query import ImageQuery


def test_openai_reranker_scores_and_rejects_off_topic(monkeypatch):
    import openai

    responses = [
        {"scores": [{"id": 1, "score": 12}, {"id": 2, "score": 94}]},
        {"scores": [{"id": 1, "score": 0}, {"id": 2, "score": 0}]},
    ]
    calls = []

    def complete(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(
            content=json.dumps(responses.pop(0))))])

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(openai, "OpenAI", lambda **kwargs: SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=complete))))
    products = [SimpleNamespace(productId=identity, productName=name,
        category=SimpleNamespace(categoryName="Laptops"), searchableText=lambda: name)
        for identity, name in ((1, "Laptop A"), (2, "Laptop B"))]

    reranker = RerankingService()
    assert reranker.rerank("portable laptop", products) == {2: 0.94}
    assert reranker.rerank("Chào bạn, bạn có khỏe không?", products) == {}
    assert calls[0]["response_format"]["type"] == "json_schema"


def test_reranker_is_used_after_candidate_retrieval(services):
    observed = []

    def rerank(query, candidates):
        observed.append((query, candidates))
        return {candidates[-1].productId: 0.86}

    services.search.service.ranking.reranker.rerank = rerank
    results = services.search.text("gaming laptop")
    assert observed and observed[0][0] == "gaming laptop"
    assert len(results) == 1
    assert results[0].product.productId == observed[0][1][-1].productId
    assert results[0].relevanceScore == Decimal("0.86")
    services.search.service.ranking.reranker.rerank = lambda query, candidates: {}
    assert services.search.voice("Chào bạn, bạn có khỏe không?") == []


def test_image_and_text_also_reranks(services):
    observed = []

    def rerank(query, candidates):
        observed.append(query)
        return {candidate.productId: 0.9 for candidate in candidates if candidate.brand == "Samsung"}

    services.search.service.ranking.reranker.rerank = rerank
    results = services.search.search(ImageQuery(imageReference="product-4.png", queryText="Samsung phone"))
    assert observed == ["samsung phone"]
    assert results and all(result.product.brand == "Samsung" for result in results)


def test_cosine_shortlist_and_display_threshold(services):
    class ControlledEmbeddings:
        @staticmethod
        def embedMany(texts):
            scores = [0.4] * 19 + [0.3] + [0.2] * (len(texts) - 21)
            return [[1.0, 0.0]] + [[score, sqrt(1 - score * score)] for score in scores]

    ranking = services.search.service.ranking
    ranking.text = ControlledEmbeddings()
    observed = []

    def rerank(query, candidates):
        observed.append([product.productId for product in candidates])
        return {candidates[0].productId: 0.49, candidates[1].productId: 0.5}

    ranking.reranker.rerank = rerank
    results = services.search.text("test query")
    assert len(observed[0]) == 20
    assert all(product_id <= 20 for product_id in observed[0])
    assert len(results) == 1
    assert results[0].product.productId == observed[0][1]
    assert results[0].relevanceScore == Decimal("0.5")


def test_image_text_shortlist_is_limited_to_twenty(services):
    class EqualImages:
        @staticmethod
        def embedMany(references):
            return [[1.0, 0.0] for _ in references]

    ranking = services.search.service.ranking
    ranking.image = EqualImages()
    observed = []

    def rerank(query, candidates):
        observed.append(candidates)
        return {candidate.productId: 0.5 for candidate in candidates}

    ranking.reranker.rerank = rerank
    results = services.search.search(ImageQuery(imageReference="product-4.png", queryText="electronics"))
    assert len(observed[0]) == 20
    assert len(results) == 20
    assert all(result.relevanceScore == Decimal("0.5") for result in results)


def test_reranker_rejects_unknown_product_id(monkeypatch):
    import openai

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(openai, "OpenAI", lambda **kwargs: SimpleNamespace(chat=SimpleNamespace(
        completions=SimpleNamespace(create=lambda **params: SimpleNamespace(choices=[
            SimpleNamespace(message=SimpleNamespace(content='{"scores":[{"id":999,"score":100}]}'))])))))
    product = SimpleNamespace(productId=1, productName="Phone",
        category=SimpleNamespace(categoryName="Smartphones"), searchableText=lambda: "Phone")
    with pytest.raises(ValueError, match="invalid reranking"):
        RerankingService().rerank("phone", [product])
