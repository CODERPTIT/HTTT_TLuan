from decimal import Decimal


class CollaborativeRecommender:
    WEIGHTS = {"VIEW": 1, "CLICK": 2, "ADD_TO_CART": 3, "PURCHASE": 5}

    def __init__(self, interactions):
        self.interactions = interactions

    def score(self, customerId, candidate) -> Decimal:
        history = self.interactions.findByCustomer(customerId)
        peers = set()
        for interaction in history:
            peers.update(item.customer.customerId for item in self.interactions.findByProduct(interaction.product.productId)
                         if item.customer.customerId != customerId)
        score = sum(self.WEIGHTS[item.interactionType] for item in self.interactions.findByProduct(candidate.productId)
                    if item.customer.customerId in peers)
        return Decimal(score) / Decimal(score + 10)

