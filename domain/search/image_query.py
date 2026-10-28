from dataclasses import dataclass
from domain.search.search_query import SearchQuery


@dataclass
class ImageQuery(SearchQuery):
    imageReference: str = ""

    @property
    def modality(self) -> str:
        return "Image"

