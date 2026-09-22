from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

import pytest

from slib_assistant.update import (
    CHECKSUM_ASSET,
    UPDATE_ASSET,
    UpdateError,
    is_newer_version,
    parse_release,
    parse_version,
    verify_sha256,
)
from slib_assistant.updater import install_package


def _release(tag: str = "v0.2.0") -> dict:
    return {
        "tag_name": tag,
        "draft": False,
        "prerelease": False,
        "html_url": "https://github.com/sepulse/slib-assistant/releases/tag/" + tag,
        "body": "Test release",
        "assets": [
            {
                "name": UPDATE_ASSET,
                "browser_download_url": "https://example.invalid/app.zip",
            },
            {
                "name": CHECKSUM_ASSET,
                "browser_download_url": "https://example.invalid/app.zip.sha256",
            },
        ],
    }


def test_semver_comparison_is_numeric():
    assert parse_version("v1.10.2") == (1, 10, 2)
    assert is_newer_version("v0.2.0", "0.1.9")
    assert not is_newer_version("v0.2.0", "0.2.0")


def test_non_semver_release_is_ignored():
    assert parse_release(_release("pre-office-rc-2026-09-22"), "0.1.0") is None


def test_new_release_requires_both_assets():
    payload = _release("v0.3.0")
    payload["assets"] = payload["assets"][:1]
    with pytest.raises(UpdateError):
        parse_release(payload, "0.2.0")


def test_new_release_is_parsed():
    info = parse_release(_release("v0.3.0"), "0.2.0")
    assert info is not None
    assert info.version == "0.3.0"
    assert info.package_url.endswith("app.zip")


def test_verify_sha256(tmp_path):
    artifact = tmp_path / "artifact.zip"
    artifact.write_bytes(b"slib-update")
    expected = hashlib.sha256(b"slib-update").hexdigest()
    assert verify_sha256(artifact, expected)
    assert not verify_sha256(artifact, "0" * 64)


def test_updater_replaces_only_slibassistant_and_keeps_backup(tmp_path):
    target = tmp_path / "SLibAssistant.exe"
    target.write_bytes(b"old")
    package = tmp_path / "SLibAssistant-Windows.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("SLibAssistant.exe", b"new")
        archive.writestr("SLibUpdater.exe", b"not-installed-by-running-updater")
    install_package(package, target)
    assert target.read_bytes() == b"new"
    assert target.with_suffix(".exe.bak").read_bytes() == b"old"


def test_updater_rejects_wrong_target_name(tmp_path):
    package = tmp_path / "SLibAssistant-Windows.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("SLibAssistant.exe", b"new")
    with pytest.raises(RuntimeError):
        install_package(package, tmp_path / "Other.exe")


def test_updater_does_not_follow_archive_member_path(tmp_path):
    target = tmp_path / "SLibAssistant.exe"
    target.write_bytes(b"old")
    package = tmp_path / "SLibAssistant-Windows.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("../../SLibAssistant.exe", b"new-safe")
    install_package(package, target)
    assert target.read_bytes() == b"new-safe"
    assert not (tmp_path.parent / "SLibAssistant.exe").exists()
