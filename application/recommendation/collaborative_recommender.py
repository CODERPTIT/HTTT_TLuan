from decimal import Decimal
from collections import defaultdict


class CollaborativeRecommender:
    WEIGHTS = {"VIEW": 1, "CLICK": 2, "ADD_TO_CART": 3, "PURCHASE": 5}
    MAX_PREFERENCE = Decimal(5)

    def __init__(self, interactions):
        self.interactions = interactions

    def score(self, sourceProductId, candidate) -> Decimal:
        return self.scores(sourceProductId, [candidate])[candidate.productId]

    def scores(self, sourceProductId, candidates) -> dict[int, Decimal]:
        matrix = defaultdict(lambda: defaultdict(Decimal))
        for interaction in self.interactions.listAll():
            interactionCustomerId = interaction.customer.customerId
            interactionProductId = interaction.product.productId
            matrix[interactionCustomerId][interactionProductId] = min(
                matrix[interactionCustomerId][interactionProductId] + self.WEIGHTS[interaction.interactionType],
                self.MAX_PREFERENCE,
            )

        source = {customerId: ratings[sourceProductId] for customerId, ratings in matrix.items()
                  if ratings.get(sourceProductId)}
        source_length = sum((value * value for value in source.values()), Decimal(0)).sqrt()
        if not source_length:
            return {candidate.productId: Decimal(0) for candidate in candidates}

        scores = {}
        for candidate in candidates:
            candidate_vector = {customerId: ratings[candidate.productId] for customerId, ratings in matrix.items()
                                if ratings.get(candidate.productId)}
            candidate_length = sum((value * value for value in candidate_vector.values()), Decimal(0)).sqrt()
            dot_product = sum((value * candidate_vector.get(customerId, 0)
                               for customerId, value in source.items()), Decimal(0))
            scores[candidate.productId] = (dot_product / (source_length * candidate_length)
                                           if dot_product and candidate_length else Decimal(0))
        return scores

