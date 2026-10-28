from domain.search.text_query import TextQuery
from domain.search.voice_query import VoiceQuery
from domain.search.image_query import ImageQuery
from domain.search.search_query import SearchQuery
from domain.search.search_result import SearchResult
from application.search.search_service import SearchService


class SearchController:
    def __init__(self, service: SearchService):
        self.service = service

    def search(self, query: SearchQuery) -> list[SearchResult]:
        return self.service.search(query)

    def _text(self, text):
        return self.search(TextQuery(queryText=text))

    def _voice(self, transcript):
        return self.search(VoiceQuery(audioReference="transcript:" + transcript, transcribedText=transcript))

    def _image(self, content, filename, content_type):
        reference = self.service._upload(content, filename, content_type)
        return reference, self.search(ImageQuery(imageReference=reference))

    def _catalog(self):
        return self.service._catalog()

    def _product(self, productId: int, customerId: int):
        return self.service._product(productId, customerId)

    def _filterResults(self, results, category="", brand="", minimum=0, maximum=None,
                       available=False, sort="relevance"):
        return self.service._filterResults(results, category, brand, minimum, maximum, available, sort)

