from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(kw_only=True)
class SearchQuery(ABC):
    searchQueryId: int = 0
    createdAt: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    @abstractmethod
    def modality(self) -> str:
        raise NotImplementedError

