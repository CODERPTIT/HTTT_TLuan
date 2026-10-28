from datetime import datetime
from decimal import Decimal
from sqlalchemy import select
from domain.search.text_query import TextQuery
from domain.search.image_query import ImageQuery
from domain.search.voice_query import VoiceQuery
from domain.search.search_result import SearchResult
from data.infrastructure.order_database import (search_queries, text_queries, image_queries,
                                                voice_queries, search_results)


class SearchRepository:
    def __init__(self, connection, products):
        self.connection = connection
        self.products = products

    def save(self, query, results: list[SearchResult], customerId: int) -> None:
        query.searchQueryId = self.connection.execute(search_queries.insert().values(
            customer_id=customerId, created_at=query.createdAt.isoformat(),
            type=query.modality.upper())).inserted_primary_key[0]
        if isinstance(query, TextQuery):
            self.connection.execute(text_queries.insert().values(
                search_query_id=query.searchQueryId, query_text=query.queryText))
        elif isinstance(query, ImageQuery):
            self.connection.execute(image_queries.insert().values(
                search_query_id=query.searchQueryId, image_reference=query.imageReference))
        elif isinstance(query, VoiceQuery):
            self.connection.execute(voice_queries.insert().values(
                search_query_id=query.searchQueryId, transcribed_text=query.transcribedText,
                audio_reference=query.audioReference))
        else:
            raise ValueError("Unsupported search modality")
        for result in results:
            self.connection.execute(search_results.insert().values(
                search_query_id=query.searchQueryId, product_id=result.product.productId,
                rank=result.rank, relevance_score=result.relevanceScore))

    def findById(self, searchQueryId: int):
        row = self.connection.execute(select(search_queries).where(
            search_queries.c.id == searchQueryId)).mappings().first()
        if row is None:
            raise LookupError("Search query not found")
        common = dict(searchQueryId=row["id"], createdAt=datetime.fromisoformat(row["created_at"]))
        if row["type"] == "TEXT":
            detail = self.connection.execute(select(text_queries).where(
                text_queries.c.search_query_id == searchQueryId)).mappings().one()
            return TextQuery(queryText=detail["query_text"], **common)
        if row["type"] == "IMAGE":
            detail = self.connection.execute(select(image_queries).where(
                image_queries.c.search_query_id == searchQueryId)).mappings().one()
            return ImageQuery(imageReference=detail["image_reference"], **common)
        if row["type"] == "VOICE":
            detail = self.connection.execute(select(voice_queries).where(
                voice_queries.c.search_query_id == searchQueryId)).mappings().one()
            return VoiceQuery(transcribedText=detail["transcribed_text"],
                              audioReference=detail["audio_reference"], **common)
        raise ValueError("Unsupported stored search modality")

    def findByCustomer(self, customerId: int) -> list:
        identities = self.connection.execute(select(search_queries.c.id).where(
            search_queries.c.customer_id == customerId).order_by(
                search_queries.c.created_at.desc(), search_queries.c.id.desc())).scalars()
        return [self.findById(identity) for identity in identities]

    def findResults(self, searchQueryId: int) -> list[SearchResult]:
        rows = self.connection.execute(select(search_results).where(
            search_results.c.search_query_id == searchQueryId).order_by(search_results.c.rank)).mappings()
        return [SearchResult(row["rank"], Decimal(row["relevance_score"]),
                             self.products.findById(row["product_id"])) for row in rows]
