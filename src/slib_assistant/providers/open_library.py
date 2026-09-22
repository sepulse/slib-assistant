from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlencode

from slib_assistant.models import ProviderRecord

from .base import MetadataProvider, ProviderNotFound
from .http import get_json


class OpenLibraryProvider(MetadataProvider):
    name = "open_library"

    def lookup(self, isbn13: str, timeout_seconds: float) -> ProviderRecord:
        fields = ",".join(
            [
                "title",
                "author_name",
                "publisher",
                "first_publish_year",
                "isbn",
                "language",
                "subject",
                "ddc",
                "number_of_pages_median",
                "publish_place",
            ]
        )
        query = urlencode(
            {"isbn": isbn13, "fields": fields, "limit": 1},
            safe=",",
        )
        payload = get_json(
            "https://openlibrary.org/search.json?" + query,
            timeout_seconds,
        )
        docs = payload.get("docs") or []
        if not docs:
            raise ProviderNotFound(isbn13)
        entry = docs[0]
        isbns = entry.get("isbn") or []
        isbn10 = next((value for value in isbns if len(value) == 10), None)
        isbn13_value = next((value for value in isbns if value == isbn13), isbn13)
        publishers = entry.get("publisher") or []
        places = entry.get("publish_place") or []
        ddc_values = entry.get("ddc") or []
        languages = entry.get("language") or []
        data = {
            "isbn13": isbn13_value,
            "isbn10": isbn10,
            "title": entry.get("title"),
            "authors": entry.get("author_name") or [],
            "publisher": publishers[0] if publishers else None,
            "publication_place": places[0] if places else None,
            "publication_year": entry.get("first_publish_year"),
            "language": languages[0] if languages else None,
            "page_count": entry.get("number_of_pages_median"),
            "subjects": entry.get("subject") or [],
            "ddc": ddc_values[0] if ddc_values else None,
        }
        return ProviderRecord(
            provider=self.name,
            isbn13=isbn13,
            data={k: v for k, v in data.items() if v not in (None, "", [])},
            raw=payload,
            fetched_at=datetime.now(timezone.utc).isoformat(),
        )
