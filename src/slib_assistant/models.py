from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    REVIEW = "REVIEW"
    MISSING = "MISSING"


class AppState(str, Enum):
    IDLE = "IDLE"
    LOOKING_UP = "LOOKING_UP"
    REVIEW = "REVIEW"
    READY_TO_FILL = "READY_TO_FILL"
    ERROR = "ERROR"
    ABORTED = "ABORTED"


@dataclass(slots=True)
class FieldConflict:
    field: str
    selected: Any
    alternatives: list[Any] = field(default_factory=list)
    sources: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderRecord:
    provider: str
    isbn13: str
    data: dict[str, Any]
    raw: dict[str, Any] = field(default_factory=dict)
    fetched_at: str = ""


@dataclass(slots=True)
class BookMetadata:
    isbn13: str
    isbn10: str | None = None
    title: str | None = None
    subtitle: str | None = None
    authors: list[str] = field(default_factory=list)
    corporate_author: str | None = None
    publisher: str | None = None
    publication_place: str | None = None
    publication_year: int | None = None
    edition: str | None = None
    language: str | None = None
    page_count: int | None = None
    physical_description: str | None = None
    dimensions: str | None = None
    series: str | None = None
    subjects: list[str] = field(default_factory=list)
    ddc: str | None = None
    lcc: str | None = None
    notes: str | None = None
    price: str | None = None
    sources: list[str] = field(default_factory=list)
    field_provenance: dict[str, list[str]] = field(default_factory=dict)
    field_confidence: dict[str, Confidence] = field(default_factory=dict)
    conflicts: list[FieldConflict] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["field_confidence"] = {
            key: value.value if isinstance(value, Confidence) else str(value)
            for key, value in self.field_confidence.items()
        }
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "BookMetadata":
        data = dict(payload)
        data["field_confidence"] = {
            key: Confidence(value)
            for key, value in data.get("field_confidence", {}).items()
        }
        data["conflicts"] = [
            item if isinstance(item, FieldConflict) else FieldConflict(**item)
            for item in data.get("conflicts", [])
        ]
        return cls(**data)
