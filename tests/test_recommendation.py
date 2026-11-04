from types import SimpleNamespace

from application.recommendation.collaborative_recommender import CollaborativeRecommender


def test_eligible_and_deterministic(services):
    first = services.recommendation.getRecommendations(1, 1)
    second = services.recommendation.getRecommendations(1, 1)
    assert first == second
    assert first
    assert all(product.productId not in {1, 24} for product in first)
    assert all(product.isAvailable(1) for product in first)


def test_cold_start(services):
    results = services.recommendation.getRecommendations(999, 1)
    assert results
    assert results[0].category.categoryName == "Laptops"


def test_collaborative_signal(services):
    service = services.recommendation.service
    candidate = service.products.findById(2)
    assert service.calculateCollaborativeScore(1, candidate) > 0


def test_item_cosine_similarity_uses_customer_interaction_columns():
    def interaction(customer_id, product_id, kind):
        return SimpleNamespace(customer=SimpleNamespace(customerId=customer_id),
                               product=SimpleNamespace(productId=product_id), interactionType=kind)

    history = [
        interaction(1, 1, "PURCHASE"), interaction(1, 2, "VIEW"),
        interaction(2, 1, "PURCHASE"), interaction(2, 2, "VIEW"), interaction(2, 3, "PURCHASE"),
        interaction(3, 1, "VIEW"), interaction(3, 2, "PURCHASE"), interaction(3, 4, "PURCHASE"),
    ]
    repository = SimpleNamespace(listAll=lambda: history)
    recommender = CollaborativeRecommender(repository)
    candidates = [SimpleNamespace(productId=3), SimpleNamespace(productId=4)]

    scores = recommender.scores(1, candidates)
    assert 0 < scores[4] < scores[3] < 1
    assert recommender.score(1, candidates[0]) == scores[3]
    assert all(score == 0 for score in recommender.scores(999, candidates).values())


def test_item_similarity_does_not_require_target_customer_history():
    def interaction(customer_id, product_id, kind):
        return SimpleNamespace(customer=SimpleNamespace(customerId=customer_id),
                               product=SimpleNamespace(productId=product_id), interactionType=kind)

    history = [interaction(1, 1, "PURCHASE"), interaction(1, 2, "ADD_TO_CART"),
               interaction(2, 1, "VIEW"), interaction(2, 2, "PURCHASE")]
    recommender = CollaborativeRecommender(SimpleNamespace(listAll=lambda: history))

    assert recommender.score(1, SimpleNamespace(productId=2)) > 0


def test_repeated_interactions_are_capped_at_maximum_preference():
    def interaction(customer_id, product_id, kind):
        return SimpleNamespace(customer=SimpleNamespace(customerId=customer_id),
                               product=SimpleNamespace(productId=product_id), interactionType=kind)

    history = [
        interaction(1, 1, "PURCHASE"), interaction(1, 2, "VIEW"),
        interaction(2, 1, "PURCHASE"), interaction(2, 2, "VIEW"), interaction(2, 3, "PURCHASE"),
    ]
    candidates = [SimpleNamespace(productId=3)]
    baseline = CollaborativeRecommender(SimpleNamespace(listAll=lambda: history)).scores(1, candidates)
    repeated = history + [interaction(1, 1, "PURCHASE") for _ in range(10)] \
        + [interaction(2, 3, "PURCHASE") for _ in range(10)]
    capped = CollaborativeRecommender(SimpleNamespace(listAll=lambda: repeated)).scores(1, candidates)

    assert capped == baseline

