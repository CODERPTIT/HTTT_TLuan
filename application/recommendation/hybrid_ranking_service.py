from decimal import Decimal


class HybridRankingService:
    def combine(self, contentScore: Decimal, collaborativeScore: Decimal) -> Decimal:
        return Decimal("0.6") * contentScore + Decimal("0.4") * collaborativeScore

    def rank(self, candidates, scores):
        return sorted(candidates, key=lambda product: (-scores.get(product.productId, Decimal(0)), product.productId))

