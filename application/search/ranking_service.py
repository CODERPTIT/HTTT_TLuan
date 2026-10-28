import re
from decimal import Decimal
from domain.search.image_query import ImageQuery
from domain.search.voice_query import VoiceQuery
from domain.search.search_result import SearchResult
from domain.search.search_query import SearchQuery
from domain.product.product import Product


class RankingService:
    def __init__(self, text, image, products, top_k: int = 100):
        self.text = text
        self.image = image
        self.products = products
        self.top_k = top_k

    def rank(self, products: list[Product], query: SearchQuery) -> list[SearchResult]:
        scores = {}
        if isinstance(query, ImageQuery):
            vector = self.image.embed(query.imageReference)
            for product in products:
                self.products._indexVector(product.productId, self.image.embed(f"product-{product.productId}.png"))
            scores = dict(self.products._searchVectors(vector))
        else:
            text = query.transcribedText if isinstance(query, VoiceQuery) else query.queryText
            budget = re.search(r"under\s+(\d+(?:\.\d+)?)\s*(million|m)?", text)
            maximum = Decimal(budget[1]) * (1000000 if budget and budget[2] else 1) if budget else None
            clean = text[:budget.start()] if budget else text
            tokens = set(self.text.tokens(clean))
            aliases = {"phone": "smartphones", "laptop": "laptops", "tv": "televisions", "headphone": "headphones"}
            tokens = {aliases.get(token, token) for token in tokens} - {"a", "the", "for", "and", "electronics"}
            vector = self.text.embed(clean)
            for product in products:
                if maximum is not None and product.price > maximum:
                    continue
                content = product.searchableText()
                product_tokens = set(self.text.tokens(content))
                overlap = len(tokens & product_tokens) / len(tokens) if tokens else 1
                if overlap == 0:
                    continue
                embedded = self.text.embed(content)
                scores[product.productId] = 0.8 * overlap + 0.2 * sum(first * second for first, second in zip(vector, embedded))
        ranked = sorted((product for product in products if product.productId in scores),
                        key=lambda product: (-scores[product.productId], product.productId))[:self.top_k]
        return [SearchResult(position, Decimal(str(round(scores[product.productId], 6))), product)
                for position, product in enumerate(ranked, 1)]

