from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import quote

from slib_assistant.models import ProviderRecord

from .base import MetadataProvider, ProviderNotFound
from .http import get_json


class GoogleBooksProvider(MetadataProvider):
    name = "google_books"

    def lookup(self, isbn13: str, timeout_seconds: float) -> ProviderRecord:
        payload = get_json(
            "https://www.googleapis.com/books/v1/volumes?q=" + quote(f"isbn:{isbn13}"),
            timeout_seconds,
        )
        items = payload.get("items") or []
        if not items:
            raise ProviderNotFound(isbn13)
        info = items[0].get("volumeInfo") or {}
        identifiers = {
            item.get("type"): item.get("identifier")
            for item in info.get("industryIdentifiers", [])
            if item.get("type") and item.get("identifier")
        }
        published = str(info.get("publishedDate") or "")
        year = int(published[:4]) if published[:4].isdigit() else None
        data = {
            "isbn13": identifiers.get("ISBN_13") or isbn13,
            "isbn10": identifiers.get("ISBN_10"),
            "title": info.get("title"),
            "subtitle": info.get("subtitle"),
            "authors": info.get("authors") or [],
            "publisher": info.get("publisher"),
            "publication_year": year,
            "language": info.get("language"),
            "page_count": info.get("pageCount"),
            "subjects": info.get("categories") or [],
        }
        return ProviderRecord(
            provider=self.name,
            isbn13=isbn13,
            data={k: v for k, v in data.items() if v not in (None, "", [])},
            raw=payload,
            fetched_at=datetime.now(timezone.utc).isoformat(),
        )
