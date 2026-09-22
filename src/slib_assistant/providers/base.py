from __future__ import annotations

from abc import ABC, abstractmethod

from slib_assistant.models import ProviderRecord


class ProviderError(RuntimeError):
    pass


class ProviderNotFound(ProviderError):
    pass


class MetadataProvider(ABC):
    name: str

    @abstractmethod
    def lookup(self, isbn13: str, timeout_seconds: float) -> ProviderRecord:
        raise NotImplementedError
