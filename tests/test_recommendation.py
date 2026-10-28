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

