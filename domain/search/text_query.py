from dataclasses import dataclass
from domain.search.search_query import SearchQuery


@dataclass
class TextQuery(SearchQuery):
    queryText: str = ""

    @property
    def modality(self) -> str:
        return "Text"

