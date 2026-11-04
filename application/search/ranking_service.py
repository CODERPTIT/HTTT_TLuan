from decimal import Decimal
from domain.search.image_query import ImageQuery
from domain.search.voice_query import VoiceQuery
from domain.search.search_result import SearchResult
from domain.search.search_query import SearchQuery
from domain.product.product import Product
from application.search.query_filter import QueryFilters


class RankingService:
    MIN_CANDIDATE_COSINE = 0.20
    MIN_DISPLAY_SCORE = 0.50

    def __init__(self, text, image, products, reranker=None, filter_extractor=None, top_k: int = 100):
        self.text = text
        self.image = image
        self.products = products
        self.reranker = reranker
        self.filter_extractor = filter_extractor
        self.top_k = top_k

    def rank(self, products: list[Product], query: SearchQuery) -> list[SearchResult]:
        scores = {}
        if isinstance(query, ImageQuery):
            image_text = query.queryText.strip()
            filters = self._filters(image_text, products)
            candidates = [product for product in products if filters.accepts(product)]
            references = [query.imageReference] + [f"product-{product.productId}.png" for product in candidates]
            vectors = self.image.embedMany(references)
            vector = vectors[0]
            for product, product_vector in zip(candidates, vectors[1:]):
                self.products.indexVector(product.productId, product_vector)
            candidate_ids = {product.productId for product in candidates}
            scores = {product_id: score for product_id, score in self.products.searchVectors(vector)
                      if product_id in candidate_ids}
            if image_text and candidates:
                eligible = {}
                text_scores = {}
                if filters.semanticText:
                    contents = [product.searchableText() for product in candidates]
                    text_vectors = self.text.embedMany([filters.semanticText] + contents)
                    text_scores = {product.productId: sum(first * second for first, second in zip(text_vectors[0], embedded))
                                   for product, embedded in zip(candidates, text_vectors[1:])}
                for product in candidates:
                    text_cosine = text_scores.get(product.productId, 0)
                    image_cosine = scores[product.productId]
                    if image_cosine > self.MIN_CANDIDATE_COSINE or text_cosine > self.MIN_CANDIDATE_COSINE:
                        eligible[product.productId] = 0.6 * image_cosine + 0.4 * text_cosine
                scores = eligible
                if self.reranker and scores:
                    shortlisted = sorted((product for product in candidates if product.productId in scores),
                        key=lambda product: (-scores[product.productId], product.productId))[:20]
                    scores = self.reranker.rerank(image_text, shortlisted)
            else:
                scores = {product_id: score for product_id, score in scores.items()
                          if score >= self.MIN_DISPLAY_SCORE}
        else:
            text = query.transcribedText if isinstance(query, VoiceQuery) else query.queryText
            filters = self._filters(text, products)
            candidates = []
            for product in products:
                if not filters.accepts(product):
                    continue
                content = product.searchableText()
                candidates.append((product, content))
            if filters.semanticText and candidates:
                vectors = self.text.embedMany([filters.semanticText] + [content for _, content in candidates])
                vector = vectors[0]
                for (product, _), embedded in zip(candidates, vectors[1:]):
                    scores[product.productId] = sum(first * second for first, second in zip(vector, embedded))
            else:
                scores = {product.productId: 1 for product, _ in candidates}

            if scores:
                if filters.semanticText:
                    scores = {product_id: score for product_id, score in scores.items()
                              if score > self.MIN_CANDIDATE_COSINE}
                if self.reranker and scores:
                    shortlisted = sorted((product for product, _ in candidates if product.productId in scores),
                        key=lambda product: (-scores[product.productId], product.productId))[:20]
                    scores = self.reranker.rerank(text, shortlisted)
        scores = {product_id: score for product_id, score in scores.items()
                  if score >= self.MIN_DISPLAY_SCORE}
        ranked = sorted((product for product in products if product.productId in scores),
                        key=lambda product: (-scores[product.productId], product.productId))[:self.top_k]
        return [SearchResult(position, Decimal(str(round(scores[product.productId], 6))), product)
                for position, product in enumerate(ranked, 1)]

    def _filters(self, text: str, products: list[Product]) -> QueryFilters:
        if self.filter_extractor and text.strip():
            return self.filter_extractor.extract(text, products)
        return QueryFilters.parse(text, products)

