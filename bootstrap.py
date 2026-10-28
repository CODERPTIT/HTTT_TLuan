from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from data.infrastructure.product_database import ProductDatabase
from data.infrastructure.order_database import OrderDatabase
from data.infrastructure.image_storage import ImageStorage
from data.infrastructure.vector_index import VectorIndex
from data.repository.product_repository import ProductRepository
from data.repository.cart_repository import CartRepository
from data.repository.interaction_repository import InteractionRepository
from data.repository.search_repository import SearchRepository
from data.repository.order_repository import OrderRepository
from data.repository.payment_repository import PaymentRepository
from data.repository.shipment_repository import ShipmentRepository
from application.search.search_service import SearchService
from application.search.query_processor import QueryProcessor
from application.search.speech_to_text_service import SpeechToTextService
from application.search.text_embedding_service import TextEmbeddingService
from application.search.image_embedding_service import ImageEmbeddingService
from application.search.retrieval_service import RetrievalService
from application.search.ranking_service import RankingService
from application.recommendation.recommendation_service import RecommendationService
from application.recommendation.content_based_recommender import ContentBasedRecommender
from application.recommendation.collaborative_recommender import CollaborativeRecommender
from application.recommendation.hybrid_ranking_service import HybridRankingService
from application.commerce.cart_service import CartService
from application.commerce.checkout_service import CheckoutService
from application.commerce.order_service import OrderService
from presentation.search_controller import SearchController
from presentation.recommendation_controller import RecommendationController
from presentation.cart_controller import CartController
from presentation.checkout_controller import CheckoutController
from presentation.order_controller import OrderController
from seeds.seed_data import seed


class Bootstrap:
    def __init__(self, root: Path):
        root.mkdir(parents=True, exist_ok=True)
        self.images = ImageStorage(root / "images")
        self.database = ProductDatabase("sqlite:///" + (root / "electronics.db").as_posix())
        self.order_database = OrderDatabase(self.database.engine)
        self.database.create()
        with self.order_database.transaction() as connection:
            seed(connection, self.images.root)

    @contextmanager
    def scope(self):
        with self.order_database.transaction() as connection:
            connection.exec_driver_sql("BEGIN IMMEDIATE")
            products = ProductRepository(connection, self.images, VectorIndex())
            interactions = InteractionRepository(connection, products)
            searches = SearchRepository(connection, products)
            carts = CartRepository(connection, products)
            orders = OrderRepository(connection, products)
            payments = PaymentRepository(connection)
            shipments = ShipmentRepository(connection)
            search = SearchService(QueryProcessor(SpeechToTextService()), RetrievalService(products),
                RankingService(TextEmbeddingService(), ImageEmbeddingService(products), products), products, interactions, searches)
            recommendation = RecommendationService(products, interactions, ContentBasedRecommender(),
                CollaborativeRecommender(interactions), HybridRankingService())
            cart = CartService(carts, products, interactions)
            checkout = CheckoutService(carts, products, orders, payments, shipments, interactions)
            order = OrderService(orders, shipments, payments)
            yield SimpleNamespace(search=SearchController(search), recommendation=RecommendationController(recommendation),
                cart=CartController(cart), checkout=CheckoutController(checkout), order=OrderController(order),
                customer=interactions._customer(1))

