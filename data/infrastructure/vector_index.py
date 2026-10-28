from math import sqrt


class VectorIndex:
    def __init__(self):
        self.vectors: dict[int, list[float]] = {}

    def store(self, productId: int, vector: list[float]) -> None:
        self.vectors[productId] = vector

    @staticmethod
    def cosine(left: list[float], right: list[float]) -> float:
        denominator = sqrt(sum(value * value for value in left) * sum(value * value for value in right))
        return sum(first * second for first, second in zip(left, right)) / denominator if denominator else 0.0

    def search(self, vector: list[float], limit: int = 100) -> list[tuple[int, float]]:
        return sorted(((identity, self.cosine(vector, stored)) for identity, stored in self.vectors.items()),
                      key=lambda pair: (-pair[1], pair[0]))[:limit]

