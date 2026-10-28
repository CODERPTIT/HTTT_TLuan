from application.recommendation.recommendation_service import RecommendationService
from domain.product.product import Product


class RecommendationController:
    def __init__(self, service: RecommendationService):
        self.service = service

    def getRecommendations(self, customerId: int, productId: int) -> list[Product]:
        return self.service.recommend(customerId, productId)

