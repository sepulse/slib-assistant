import json
from urllib.error import HTTPError

import pytest

import slib_assistant.providers.google_books as google_module
import slib_assistant.providers.http as http_module
import slib_assistant.providers.open_library as open_module
from slib_assistant.providers import GoogleBooksProvider, OpenLibraryProvider
from slib_assistant.providers.base import ProviderError, ProviderNotFound


def test_google_books_partial_result_preserves_missing(monkeypatch):
    monkeypatch.setattr(
        google_module,
        "get_json",
        lambda *_args, **_kwargs: {
            "items": [{"volumeInfo": {"title": "Partial", "authors": ["A"]}}]
        },
    )
    record = GoogleBooksProvider().lookup("9789836276964", 5)
    assert record.data["title"] == "Partial"
    assert "publisher" not in record.data


def test_open_library_current_search_shape(monkeypatch):
    monkeypatch.setattr(
        open_module,
        "get_json",
        lambda *_args, **_kwargs: {
            "docs": [
                {
                    "title": "Buku",
                    "author_name": ["Ali"],
                    "publisher": ["DBP"],
                    "first_publish_year": 2020,
                    "isbn": ["9789836276964"],
                    "ddc": ["510"],
                }
            ]
        },
    )
    record = OpenLibraryProvider().lookup("9789836276964", 5)
    assert record.data["publisher"] == "DBP"
    assert record.data["ddc"] == "510"


def test_open_library_not_found(monkeypatch):
    monkeypatch.setattr(open_module, "get_json", lambda *_args, **_kwargs: {"docs": []})
    with pytest.raises(ProviderNotFound):
        OpenLibraryProvider().lookup("9789836276964", 5)


def test_http_429_becomes_provider_error(monkeypatch):
    def fail(*_args, **_kwargs):
        raise HTTPError("https://example.invalid", 429, "Too Many Requests", {}, None)

    monkeypatch.setattr(http_module, "urlopen", fail)
    with pytest.raises(ProviderError, match="HTTP 429"):
        http_module.get_json("https://example.invalid", 1)


def test_malformed_json_becomes_provider_error(monkeypatch):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return b"{not-json"

    monkeypatch.setattr(http_module, "urlopen", lambda *_args, **_kwargs: Response())
    with pytest.raises(ProviderError):
        http_module.get_json("https://example.invalid", 1)
