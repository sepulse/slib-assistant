from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from slib_assistant.cache import MetadataCache
from slib_assistant.config import AppConfig, load_config
from slib_assistant.isbn import normalize_isbn
from slib_assistant.models import BookMetadata, ProviderRecord
from slib_assistant.providers import (
    GoogleBooksProvider,
    MetadataProvider,
    OpenLibraryProvider,
    ProviderError,
)
from slib_assistant.resolver import resolve_records


class MetadataService:
    def __init__(
        self,
        config: AppConfig,
        cache: MetadataCache,
        providers: list[MetadataProvider] | None = None,
    ):
        self.config = config
        self.cache = cache
        self.providers = providers if providers is not None else self._default_providers()

    def _default_providers(self) -> list[MetadataProvider]:
        result: list[MetadataProvider] = []
        if self.config.providers.get("google_books", True):
            result.append(GoogleBooksProvider())
        if self.config.providers.get("open_library", True):
            result.append(OpenLibraryProvider())
        return result

    def lookup(self, raw_isbn: str, force_refresh: bool = False) -> BookMetadata:
        normalized = normalize_isbn(raw_isbn)
        if not force_refresh:
            cached = self.cache.get(normalized.isbn13, self.config.cache_ttl_days)
            if cached is not None:
                self.cache.log_lookup(normalized.isbn13, "cache_hit")
                return cached

        records: list[ProviderRecord] = []
        if self.providers:
            with ThreadPoolExecutor(max_workers=len(self.providers)) as executor:
                futures = {
                    executor.submit(
                        provider.lookup,
                        normalized.isbn13,
                        self.config.timeout_seconds,
                    ): provider
                    for provider in self.providers
                }
                for future in as_completed(futures):
                    provider = futures[future]
                    try:
                        records.append(future.result())
                    except ProviderError:
                        logging.info("Provider failed: %s", provider.name)
                    except Exception:
                        logging.exception("Provider failed unexpectedly: %s", provider.name)

        metadata = resolve_records(normalized.isbn13, records)
        if metadata.isbn10 is None:
            metadata.isbn10 = normalized.isbn10
            if normalized.isbn10:
                metadata.field_provenance["isbn10"] = ["isbn_checksum"]
        self.cache.put(metadata, records)
        self.cache.log_lookup(
            normalized.isbn13, "resolved" if records else "no_metadata"
        )
        return metadata


def main() -> int:
    config = load_config()
    config.data_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        filename=config.data_dir / "slib-assistant.log",
        format="%(asctime)s %(levelname)s %(message)s",
    )
    cache = MetadataCache(config.data_dir / "metadata.sqlite3")
    service = MetadataService(config, cache)
    from slib_assistant.ui.main_window import run_ui
    run_ui(config, service)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
