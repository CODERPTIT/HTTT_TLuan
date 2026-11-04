from types import SimpleNamespace
import pytest
import openai
from application.search.text_embedding_service import TextEmbeddingService


def test_openai_embeds_query_and_product_with_one_model(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    monkeypatch.setattr(TextEmbeddingService, "_vectors", {})
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(data=[SimpleNamespace(index=index, embedding=[float(index), 1.0])
                                     for index, _ in enumerate(kwargs["input"])])

    monkeypatch.setattr(openai, "OpenAI", lambda **kwargs: SimpleNamespace(
        embeddings=SimpleNamespace(create=create)))
    service = TextEmbeddingService()
    assert service.embedMany(["chuột", "Wireless mouse"]) == [[0.0, 1.0], [1.0, 1.0]]
    assert calls[0] == {"model": "text-embedding-3-small", "input": ["chuột", "Wireless mouse"]}
    assert service.embedMany(["chuột không dây", "Wireless mouse"]) == [[0.0, 1.0], [1.0, 1.0]]
    assert calls[1]["input"] == ["chuột không dây"]


def test_text_search_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        TextEmbeddingService().embed("mouse")
