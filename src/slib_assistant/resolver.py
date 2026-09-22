from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from slib_assistant.models import BookMetadata, Confidence, FieldConflict, ProviderRecord


SCALAR_FIELDS = (
    "isbn10",
    "title",
    "subtitle",
    "corporate_author",
    "publisher",
    "publication_place",
    "publication_year",
    "edition",
    "language",
    "page_count",
    "physical_description",
    "dimensions",
    "series",
    "ddc",
    "lcc",
    "notes",
    "price",
)
LIST_FIELDS = ("authors", "subjects")


def _norm(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip().casefold()


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        key = _norm(value)
        if key and key not in seen:
            seen.add(key)
            output.append(re.sub(r"\s+", " ", value).strip())
    return output


def resolve_records(isbn13: str, records: list[ProviderRecord]) -> BookMetadata:
    metadata = BookMetadata(isbn13=isbn13)
    metadata.sources = [record.provider for record in records]
    by_field: dict[str, list[tuple[str, Any]]] = defaultdict(list)
    for record in records:
        for key, value in record.data.items():
            if value not in (None, "", []):
                by_field[key].append((record.provider, value))

    for field_name in SCALAR_FIELDS:
        candidates = by_field.get(field_name, [])
        if not candidates:
            metadata.field_confidence[field_name] = Confidence.MISSING
            continue
        grouped: dict[str, list[tuple[str, Any]]] = defaultdict(list)
        for provider, value in candidates:
            grouped[_norm(value)].append((provider, value))
        selected_group = max(grouped.values(), key=len)
        selected = selected_group[0][1]
        setattr(metadata, field_name, selected)
        metadata.field_provenance[field_name] = [p for p, _ in selected_group]
        if len(grouped) == 1:
            metadata.field_confidence[field_name] = (
                Confidence.HIGH if len(selected_group) >= 2 else Confidence.MEDIUM
            )
        else:
            metadata.field_confidence[field_name] = Confidence.REVIEW
            metadata.conflicts.append(
                FieldConflict(
                    field=field_name,
                    selected=selected,
                    alternatives=[
                        group[0][1]
                        for group in grouped.values()
                        if group is not selected_group
                    ],
                    sources={provider: value for provider, value in candidates},
                )
            )

    for field_name in LIST_FIELDS:
        candidates = by_field.get(field_name, [])
        merged: list[str] = []
        sources: list[str] = []
        for provider, values in candidates:
            if isinstance(values, (list, tuple)):
                merged.extend(str(value) for value in values if value)
                sources.append(provider)
        final = _dedupe(merged)
        setattr(metadata, field_name, final)
        metadata.field_provenance[field_name] = list(dict.fromkeys(sources))
        metadata.field_confidence[field_name] = (
            Confidence.MISSING
            if not final
            else Confidence.HIGH
            if len(set(sources)) >= 2
            else Confidence.MEDIUM
        )

    metadata.field_provenance["isbn13"] = list(dict.fromkeys(metadata.sources))
    metadata.field_confidence["isbn13"] = Confidence.HIGH
    return metadata
