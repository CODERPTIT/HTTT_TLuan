from conftest import fake_embed_many, fake_extract_filters
from application.search.text_embedding_service import TextEmbeddingService
from application.search.reranking_service import RerankingService
from application.search.query_filter_extraction_service import QueryFilterExtractionService

TextEmbeddingService.embedMany = fake_embed_many
RerankingService.rerank = lambda self, query, candidates: {
    product.productId: 1 - index / 100 for index, product in enumerate(candidates)}
QueryFilterExtractionService.extract = fake_extract_filters

from main import app
