from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_CONFIG = """[slib]
window_title = "Kemaskini Bahan"
auto_save = false

[lookup]
timeout_seconds = 5
cache_ttl_days = 30

[providers]
google_books = true
open_library = true
marc_sru = false

[logging]
level = "INFO"
"""


def default_data_dir() -> Path:
    root = os.environ.get("LOCALAPPDATA")
    if root:
        return Path(root) / "SLibAssistant"
    return Path.home() / ".slib-assistant"


@dataclass(slots=True)
class AppConfig:
    window_title: str = "Kemaskini Bahan"
    auto_save: bool = False
    timeout_seconds: float = 5.0
    cache_ttl_days: int = 30
    providers: dict[str, bool] = field(
        default_factory=lambda: {
            "google_books": True,
            "open_library": True,
            "marc_sru": False,
        }
    )
    log_level: str = "INFO"
    data_dir: Path = field(default_factory=default_data_dir)


def load_config(path: str | Path | None = None) -> AppConfig:
    config = AppConfig()
    candidate = Path(path) if path is not None else config.data_dir / "config.toml"
    if not candidate.exists():
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_text(DEFAULT_CONFIG, encoding="utf-8")
        return config
    payload = tomllib.loads(candidate.read_text(encoding="utf-8"))
    slib = payload.get("slib", {})
    lookup = payload.get("lookup", {})
    config.window_title = str(slib.get("window_title", config.window_title))
    config.auto_save = bool(slib.get("auto_save", False))
    if config.auto_save:
        raise ValueError("auto_save=true tidak dibenarkan dalam V1.")
    config.timeout_seconds = float(
        lookup.get("timeout_seconds", config.timeout_seconds)
    )
    config.cache_ttl_days = int(
        lookup.get("cache_ttl_days", config.cache_ttl_days)
    )
    config.providers.update(
        {key: bool(value) for key, value in payload.get("providers", {}).items()}
    )
    config.log_level = str(payload.get("logging", {}).get("level", config.log_level))
    return config
