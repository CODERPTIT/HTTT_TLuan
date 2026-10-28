import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_layer_dependencies():
    for layer in ["domain", "application", "presentation", "data"]:
        for path in (ROOT / layer).rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    imports.append(node.module or "")
                elif isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
            for imported in imports:
                if layer == "domain":
                    assert imported.split(".")[0] not in {"data", "application", "presentation", "fastapi", "sqlalchemy"}, path
                if layer == "presentation":
                    assert imported.split(".")[0] not in {"data", "sqlalchemy"}, path
                if layer == "application":
                    assert not imported.startswith(("data.infrastructure", "presentation", "fastapi")), path
                if layer == "data":
                    assert not imported.startswith(("application", "presentation")), path


def test_required_classes():
    expected = {
        "presentation": "SearchController RecommendationController CartController CheckoutController OrderController",
        "application/search": "SearchService QueryProcessor SpeechToTextService TextEmbeddingService ImageEmbeddingService RetrievalService RankingService",
        "application/recommendation": "RecommendationService ContentBasedRecommender CollaborativeRecommender HybridRankingService",
        "application/commerce": "CartService CheckoutService OrderService",
        "domain": "Customer SearchQuery TextQuery ImageQuery VoiceQuery SearchResult Product ProductSpecification Category ProductUnit Interaction Cart CartItem Order OrderItem Payment Shipment",
        "data/repository": "ProductRepository InteractionRepository SearchRepository CartRepository OrderRepository PaymentRepository ShipmentRepository",
        "data/infrastructure": "ProductDatabase OrderDatabase VectorIndex ImageStorage",
    }
    for package, names in expected.items():
        actual = {node.name for path in (ROOT / package).rglob("*.py")
                  for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))) if isinstance(node, ast.ClassDef)}
        assert set(names.split()) <= actual, package

