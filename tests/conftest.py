import hashlib
import re
import sys
from math import sqrt
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bootstrap import Bootstrap
from application.search.text_embedding_service import TextEmbeddingService
from application.search.reranking_service import RerankingService
from application.search.query_filter import QueryFilters
from application.search.query_filter_extraction_service import QueryFilterExtractionService


def fake_embed_many(self, texts):
    self.backend = "openai"
    vectors = []
    for text in texts:
        normalized = " ".join(self.tokens(text))
        for source, target in {
            "chuot khong day": "wireless mouse",
            "dien thoai": "smartphones",
            "tai nghe": "headphones",
            "man hinh": "monitor",
            "chuot": "mouse",
        }.items():
            normalized = re.sub(rf"\b{source}\b", target, normalized)
        aliases = {"phone": "smartphones", "phones": "smartphones",
                   "smartphone": "smartphones", "laptop": "laptops"}
        vector = [0.0] * 1024
        for token in normalized.split():
            token = aliases.get(token, token)
            position = int.from_bytes(hashlib.sha256(token.encode()).digest()[:4], "big") % len(vector)
            vector[position] += 3 if token in {"laptops", "smartphones", "headphones", "mouse", "monitor",
                                              "television", "gaming", "rtx", "4060"} else 1
        length = sqrt(sum(value * value for value in vector)) or 1
        vectors.append([value / length for value in vector])
    return vectors


def fake_rerank(self, query, candidates):
    return {product.productId: 1 - index / 100 for index, product in enumerate(candidates)}


def fake_extract_filters(self, query, products):
    return QueryFilters.parse(query, products)


@pytest.fixture
def container(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(TextEmbeddingService, "embedMany", fake_embed_many)
    monkeypatch.setattr(RerankingService, "rerank", fake_rerank)
    monkeypatch.setattr(QueryFilterExtractionService, "extract", fake_extract_filters)
    monkeypatch.setenv("AI_IMAGE_MODE", "basic")
    monkeypatch.setenv("AI_DETECT_MODE", "off")
    instance = Bootstrap(tmp_path)
    yield instance
    instance.database.engine.dispose()


@pytest.fixture
def services(container):
    with container.scope() as scope:
        yield scope


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("ABC_RUNTIME", str(tmp_path / "default"))
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(TextEmbeddingService, "embedMany", fake_embed_many)
    monkeypatch.setattr(RerankingService, "rerank", fake_rerank)
    monkeypatch.setattr(QueryFilterExtractionService, "extract", fake_extract_filters)
    monkeypatch.setenv("AI_IMAGE_MODE", "basic")
    monkeypatch.setenv("AI_DETECT_MODE", "off")
    from main import create_app
    from fastapi.testclient import TestClient
    app = create_app(tmp_path / "web")
    with TestClient(app) as test_client:
        response = test_client.post("/login", data={"email": "demo1@example.test", "password": "DemoCustomer123!"})
        assert response.status_code == 200
        yield test_client
    app.state.container.database.engine.dispose()

