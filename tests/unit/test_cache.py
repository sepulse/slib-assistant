from slib_assistant.cache import MetadataCache
from slib_assistant.models import BookMetadata
import sqlite3


def test_cache_roundtrip(tmp_path):
    cache = MetadataCache(tmp_path / "cache.sqlite3")
    book = BookMetadata(isbn13="9789836276964", title="Test")
    cache.put(book, [])
    loaded = cache.get(book.isbn13, ttl_days=30)
    assert loaded is not None
    assert loaded.title == "Test"


def test_stale_cache_returns_none(tmp_path):
    path = tmp_path / "cache.sqlite3"
    cache = MetadataCache(path)
    book = BookMetadata(isbn13="9789836276964", title="Old")
    cache.put(book, [])
    with sqlite3.connect(path) as db:
        db.execute(
            "UPDATE books SET updated_at = ? WHERE isbn13 = ?",
            ("2000-01-01T00:00:00+00:00", book.isbn13),
        )
    assert cache.get(book.isbn13, ttl_days=30) is None
