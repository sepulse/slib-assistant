from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from slib_assistant import __version__


REPO_SLUG = "sepulse/slib-assistant"
LATEST_RELEASE_API = f"https://api.github.com/repos/{REPO_SLUG}/releases/latest"
UPDATE_ASSET = "SLibAssistant-Windows.zip"
CHECKSUM_ASSET = UPDATE_ASSET + ".sha256"
USER_AGENT = f"SLibAssistant/{__version__}"


class UpdateError(RuntimeError):
    pass


@dataclass(slots=True, frozen=True)
class UpdateInfo:
    version: str
    tag: str
    package_url: str
    checksum_url: str
    release_url: str
    notes: str = ""


def parse_version(value: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", value.strip())
    if not match:
        raise ValueError(f"Versi tidak sah: {value}")
    return tuple(int(part) for part in match.groups())


def is_newer_version(candidate: str, current: str = __version__) -> bool:
    return parse_version(candidate) > parse_version(current)


def _request_bytes(url: str, timeout: float = 8.0) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise UpdateError(f"Tidak dapat menghubungi pelayan kemas kini: {exc}") from exc


def parse_release(payload: dict, current: str = __version__) -> UpdateInfo | None:
    if payload.get("draft") or payload.get("prerelease"):
        return None
    tag = str(payload.get("tag_name", "")).strip()
    try:
        if not is_newer_version(tag, current):
            return None
        version = tag.removeprefix("v")
    except ValueError:
        return None

    assets = {
        str(asset.get("name")): asset
        for asset in payload.get("assets", [])
        if isinstance(asset, dict)
    }
    package = assets.get(UPDATE_ASSET)
    checksum = assets.get(CHECKSUM_ASSET)
    if not package or not checksum:
        raise UpdateError(
            "Release baharu ditemui tetapi pakej kemas kini lengkap tidak tersedia."
        )
    package_url = str(package.get("browser_download_url") or "")
    checksum_url = str(checksum.get("browser_download_url") or "")
    if not package_url or not checksum_url:
        raise UpdateError("URL pakej kemas kini tidak lengkap.")

    return UpdateInfo(
        version=version,
        tag=tag,
        package_url=package_url,
        checksum_url=checksum_url,
        release_url=str(payload.get("html_url") or ""),
        notes=str(payload.get("body") or "").strip(),
    )


def check_for_update(
    current: str = __version__, timeout: float = 8.0
) -> UpdateInfo | None:
    try:
        payload = json.loads(_request_bytes(LATEST_RELEASE_API, timeout).decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise UpdateError("Respons kemas kini tidak sah.") from exc
    if not isinstance(payload, dict):
        raise UpdateError("Respons kemas kini tidak sah.")
    return parse_release(payload, current=current)


def _expected_sha256(checksum_text: str) -> str:
    match = re.search(r"\b([0-9a-fA-F]{64})\b", checksum_text)
    if not match:
        raise UpdateError("Fail checksum release tidak sah.")
    return match.group(1).lower()


def verify_sha256(path: Path, expected: str) -> bool:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().lower() == expected.lower()


def download_update(
    info: UpdateInfo, data_dir: Path, timeout: float = 30.0
) -> Path:
    update_dir = data_dir / "updates" / info.version
    update_dir.mkdir(parents=True, exist_ok=True)
    package_path = update_dir / UPDATE_ASSET
    checksum_text = _request_bytes(info.checksum_url, timeout).decode(
        "utf-8", errors="strict"
    )
    expected = _expected_sha256(checksum_text)

    temp_fd, temp_name = tempfile.mkstemp(
        prefix="slib-update-", suffix=".zip", dir=update_dir
    )
    os.close(temp_fd)
    temp_path = Path(temp_name)
    try:
        temp_path.write_bytes(_request_bytes(info.package_url, timeout))
        if not verify_sha256(temp_path, expected):
            raise UpdateError(
                "Pengesahan SHA256 gagal. Pakej kemas kini tidak akan dipasang."
            )
        temp_path.replace(package_path)
    finally:
        temp_path.unlink(missing_ok=True)
    return package_path


def packaged_runtime() -> bool:
    return bool(getattr(sys, "frozen", False))


def updater_path() -> Path:
    if not packaged_runtime():
        raise UpdateError("Auto-update hanya tersedia pada Windows build.")
    candidate = Path(sys.executable).resolve().with_name("SLibUpdater.exe")
    if not candidate.exists():
        raise UpdateError(
            "SLibUpdater.exe tidak ditemui. Pasang pakej S-Lib Assistant terkini."
        )
    return candidate


def launch_updater(package_path: Path) -> None:
    updater = updater_path()
    target = Path(sys.executable).resolve()
    subprocess.Popen(
        [
            str(updater),
            "--package",
            str(package_path.resolve()),
            "--target",
            str(target),
            "--pid",
            str(os.getpid()),
        ],
        close_fds=True,
    )
