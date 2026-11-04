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

    def text(self, text):
        return self.search(TextQuery(queryText=text))

    def voice(self, transcript):
        return self.search(VoiceQuery(audioReference="transcript:" + transcript, transcribedText=transcript))

    def image(self, content, filename, content_type, query_text="", crop_box=None):
        reference = self.uploadImage(content, filename, content_type, crop_box)
        return reference, self.search(ImageQuery(imageReference=reference, queryText=query_text))

    def uploadImage(self, content, filename, content_type, crop_box=None):
        reference = self.service.upload(content, filename, content_type)
        return self.service.crop(reference, crop_box) if crop_box is not None else reference

    def catalog(self):
        return self.service.catalog()

    def product(self, productId: int, customerId: int | None):
        return self.service.getProduct(productId, customerId)

    def filterResults(self, results, category="", brand="", minimum=0, maximum=None,
                      available=False, sort="relevance", color=""):
        return self.service.filterResults(results, category, brand, minimum, maximum, available, sort, color)

