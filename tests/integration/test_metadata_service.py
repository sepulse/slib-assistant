from slib_assistant.app import MetadataService
from slib_assistant.cache import MetadataCache
from slib_assistant.config import AppConfig
from slib_assistant.models import ProviderRecord
from slib_assistant.providers.base import MetadataProvider, ProviderError


class GoodProvider(MetadataProvider):
    name = "good"

    def __init__(self):
        self.calls = 0

    def lookup(self, isbn13, timeout_seconds):
        self.calls += 1
        return ProviderRecord(self.name, isbn13, {"title": "Resolved"})


class FailingProvider(MetadataProvider):
    name = "bad"

    def lookup(self, isbn13, timeout_seconds):
        raise ProviderError("timeout")


def test_provider_failure_isolated(tmp_path):
    config = AppConfig(data_dir=tmp_path)
    cache = MetadataCache(tmp_path / "cache.sqlite3")
    service = MetadataService(config, cache, [FailingProvider(), GoodProvider()])
    result = service.lookup("9789836276964")
    assert result.title == "Resolved"
    assert result.sources == ["good"]


def test_offline_cache_hit(tmp_path):
    config = AppConfig(data_dir=tmp_path)
    cache = MetadataCache(tmp_path / "cache.sqlite3")
    service = MetadataService(config, cache, [GoodProvider()])
    first = service.lookup("9789836276964")
    offline = MetadataService(config, cache, [FailingProvider()])
    second = offline.lookup("9789836276964")
    assert second.title == first.title


def test_force_refresh_bypasses_cache(tmp_path):
    config = AppConfig(data_dir=tmp_path)
    cache = MetadataCache(tmp_path / "cache.sqlite3")
    provider = GoodProvider()
    service = MetadataService(config, cache, [provider])
    service.lookup("9789836276964")
    service.lookup("9789836276964")
    assert provider.calls == 1
    service.lookup("9789836276964", force_refresh=True)
    assert provider.calls == 2
