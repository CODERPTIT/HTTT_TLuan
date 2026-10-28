from domain.search.text_query import TextQuery
from domain.search.voice_query import VoiceQuery
from domain.search.image_query import ImageQuery
from domain.search.search_query import SearchQuery


class QueryProcessor:
    def __init__(self, speech):
        self.speech = speech

    def process(self, query: SearchQuery) -> SearchQuery:
        if isinstance(query, TextQuery):
            query.queryText = " ".join(query.queryText.split()).lower()
        elif isinstance(query, VoiceQuery):
            query.transcribedText = " ".join((query.transcribedText or self.speech.transcribe(query.audioReference)).split()).lower()
        elif not isinstance(query, ImageQuery):
            raise ValueError("Unsupported search modality")
        return query

