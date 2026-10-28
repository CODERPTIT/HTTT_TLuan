from decimal import Decimal
from domain.product.product import Product
from domain.interaction.interaction import Interaction


class RecommendationService:
    def __init__(self, products, interactions, content, collaborative, hybrid):
        self.products = products
        self.interactions = interactions
        self.content = content
        self.collaborative = collaborative
        self.hybrid = hybrid
        self.scores = {}

    def recommend(self, customerId: int, productId: int) -> list[Product]:
        source = self.products.findById(productId)
        candidates = self.filterEligibleProducts(self.generateCandidates(productId), productId)
        collaborative_scores = {candidate.productId: self.calculateCollaborativeScore(customerId, candidate) for candidate in candidates}
        has_data = any(collaborative_scores.values())
        self.scores = {}
        for candidate in candidates:
            content = self.calculateContentScore(source, candidate)
            self.scores[candidate.productId] = self.calculateHybridScore(content, collaborative_scores[candidate.productId]) if has_data else content
        return self.rankCandidates(candidates)[:4]

    def generateCandidates(self, productId: int) -> list[Product]:
        return self.products.findEligibleProducts()

    def getInteractionHistory(self, customerId: int) -> list[Interaction]:
        return self.interactions.findByCustomer(customerId)

    def calculateContentScore(self, source: Product, candidate: Product) -> Decimal:
        return self.content.score(source, candidate)

    def calculateCollaborativeScore(self, customerId: int, candidate: Product) -> Decimal:
        return self.collaborative.score(customerId, candidate)

    def calculateHybridScore(self, contentScore: Decimal, collaborativeScore: Decimal) -> Decimal:
        return self.hybrid.combine(contentScore, collaborativeScore)

    def filterEligibleProducts(self, products: list[Product], viewedProductId: int) -> list[Product]:
        return [product for product in products if product.productId != viewedProductId
                and product.status == "ACTIVE" and product.isAvailable(1)]

    def rankCandidates(self, candidates: list[Product]) -> list[Product]:
        return self.hybrid.rank(candidates, self.scores)

