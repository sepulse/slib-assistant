from __future__ import annotations

from dataclasses import dataclass

from slib_assistant.models import ProviderRecord
from slib_assistant.providers.base import MetadataProvider, ProviderError


@dataclass(slots=True)
class SRUEndpoint:
    base_url: str
    database: str = "default"
    isbn_index: str = "bath.isbn"


class MARCSRUProvider(MetadataProvider):
    """Contract for MARC/SRU integration.

    V1 keeps this provider disabled until a reliable endpoint and mapping are
    selected. Returning fabricated bibliographic fields is never allowed.
    """

    name = "marc_sru"

    def __init__(self, endpoint: SRUEndpoint | None = None):
        self.endpoint = endpoint

    def lookup(self, isbn13: str, timeout_seconds: float) -> ProviderRecord:
        raise ProviderError(
            "MARC/SRU endpoint belum dikonfigurasi; provider sengaja tidak aktif."
        )
