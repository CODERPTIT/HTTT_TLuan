import json
from types import SimpleNamespace

import pytest

from application.search.query_filter_extraction_service import QueryFilterExtractionService


REAL_EXTRACT = QueryFilterExtractionService.extract


def _mock_openai(monkeypatch, payload):
    import openai

    calls = []

    def complete(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(
            content=json.dumps(payload)))])

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(openai, "OpenAI", lambda **kwargs: SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=complete))))
    return calls


def test_llm_extracts_structured_filters_and_regex_price_wins(services, monkeypatch):
    calls = _mock_openai(monkeypatch, {
        "semanticQuery": "long battery life",
        "minimumPrice": None,
        "maximumPrice": 20000000,
        "brands": ["Samsung"],
        "categories": ["Smartphones"],
        "colors": ["blue"],
        "availableOnly": True,
    })
    extractor = QueryFilterExtractionService()
    filters = REAL_EXTRACT(extractor, "Samsung phone màu xanh dưới 10 triệu pin lâu", services.search.catalog())
    assert filters.semanticText == "long battery life"
    assert filters.maximumPrice == 10000000
    assert filters.brands == {"Samsung"}
    assert filters.categories == {"Smartphones"}
    assert filters.colors == {"blue"}
    assert filters.availableOnly is True
    assert calls[0]["response_format"]["type"] == "json_schema"


def test_llm_filter_values_must_exist_in_catalog(services, monkeypatch):
    _mock_openai(monkeypatch, {
        "semanticQuery": "phone",
        "minimumPrice": None,
        "maximumPrice": None,
        "brands": [],
        "categories": ["Clothing"],
        "colors": [],
        "availableOnly": False,
    })
    with pytest.raises(ValueError, match="outside the product catalog"):
        REAL_EXTRACT(QueryFilterExtractionService(), "something useful", services.search.catalog())


def test_llm_filter_response_is_complete(services, monkeypatch):
    _mock_openai(monkeypatch, {"semanticQuery": "phone"})
    with pytest.raises(ValueError, match="invalid search filters"):
        REAL_EXTRACT(QueryFilterExtractionService(), "phone", services.search.catalog())

