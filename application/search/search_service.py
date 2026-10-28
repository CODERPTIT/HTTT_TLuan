from domain.search.text_query import TextQuery
from domain.search.image_query import ImageQuery
from domain.search.voice_query import VoiceQuery
from domain.search.search_query import SearchQuery
from domain.search.search_result import SearchResult
from domain.product.product import Product


class SearchService:
    def __init__(self, processor, retrieval, ranking, products, interactions, searches, customerId: int = 1):
        self.processor = processor
        self.retrieval = retrieval
        self.ranking = ranking
        self.products = products
        self.interactions = interactions
        self.searches = searches
        self.customerId = customerId

    def search(self, query: SearchQuery) -> list[SearchResult]:
        if not self.validateInput(query):
            raise ValueError("Enter a search query of up to 500 characters")
        processed = self.processQuery(query)
        results = self.rankResults(self.retrieveProducts(processed), processed)
        self.searches.save(processed, results, self.customerId)
        return results

    def validateInput(self, query: SearchQuery) -> bool:
        if isinstance(query, TextQuery):
            return bool(query.queryText.strip()) and len(query.queryText) <= 500
        if isinstance(query, VoiceQuery):
            return bool(query.transcribedText.strip() or query.audioReference.strip()) and max(len(query.transcribedText), len(query.audioReference)) <= 1000
        return isinstance(query, ImageQuery) and bool(query.imageReference)

    def processQuery(self, query: SearchQuery) -> SearchQuery:
        return self.processor.process(query)

    def retrieveProducts(self, query: SearchQuery) -> list[Product]:
        return self.retrieval.retrieve(query)

    def rankResults(self, products: list[Product], query: SearchQuery) -> list[SearchResult]:
        return self.ranking.rank(products, query)

    def _upload(self, content: bytes, filename: str, content_type: str) -> str:
        return self.products._saveImage(content, filename, content_type)

    def _catalog(self):
        return self.products.findRelevant(None)

    def _product(self, productId: int, customerId: int):
        from domain.interaction.interaction import InteractionType
        product = self.products.findById(productId)
        self.interactions._record(customerId, product, InteractionType.VIEW)
        return product

    def _filterResults(self, results, category="", brand="", minimum=0, maximum=None, available=False, sort="relevance"):
        filtered = [result for result in results
                    if (not category or result.product.category.categoryName == category)
                    and (not brand or result.product.brand == brand)
                    and result.product.price >= minimum
                    and (maximum is None or result.product.price <= maximum)
                    and (not available or (result.product.status == "ACTIVE" and result.product.isAvailable(1)))]
        if sort in {"price_asc", "price_desc"}:
            filtered.sort(key=lambda result: (result.product.price, result.product.productId), reverse=sort == "price_desc")
        return filtered

