from dataclasses import dataclass
from domain.search.search_query import SearchQuery


@dataclass
class VoiceQuery(SearchQuery):
    audioReference: str = ""
    transcribedText: str = ""

    @property
    def modality(self) -> str:
        return "Voice"

