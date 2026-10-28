from decimal import Decimal
import re


class ContentBasedRecommender:
    def score(self, source, candidate) -> Decimal:
        left = set(re.findall(r"\w+", source.searchableText().lower()))
        right = set(re.findall(r"\w+", candidate.searchableText().lower()))
        text = Decimal(len(left & right)) / max(len(left | right), 1)
        price = Decimal(1) - abs(source.price - candidate.price) / max(source.price, candidate.price, 1)
        return (Decimal("0.4") * (source.category.categoryId == candidate.category.categoryId)
                + Decimal("0.2") * (source.brand == candidate.brand) + Decimal("0.2") * text + Decimal("0.2") * price)

