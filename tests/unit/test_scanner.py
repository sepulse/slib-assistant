import os
import time

import pytest

import slib_assistant.scanner as scanner
from slib_assistant.scanner import appended_scan_matches, clean_scan, valid_scanned_isbn


def test_clean_scan_accepts_common_barcode_formatting():
    assert clean_scan("978-983-62-7696-4\r\n") == "9789836276964"


def test_valid_fast_isbn13():
    assert valid_scanned_isbn("9789836276964", 0.15) == "9789836276964"


def test_slow_typing_is_not_treated_as_scanner():
    assert valid_scanned_isbn("9789836276964", 3.0) is None


def test_invalid_checksum_is_not_routed():
    assert valid_scanned_isbn("9789836276965", 0.1) is None


def test_appended_scan_must_match_exact_original_prefix():
    assert appended_scan_matches("ABC9789836276964", "ABC", "9789836276964")
    assert not appended_scan_matches("XYZ9789836276964", "ABC", "9789836276964")
    assert not appended_scan_matches("ABC9789836276965", "ABC", "9789836276964")


@pytest.mark.skipif(os.name != "nt", reason="Windows control polling behavior")
def test_windows_backend_routes_stable_valid_isbn_without_keyboard_hook(monkeypatch):
    routed: list[str] = []
    backend = scanner._WindowsScannerBackend(
        is_enabled=lambda: True,
        on_scan=routed.append,
        on_status=lambda _message: None,
    )
    monkeypatch.setattr(backend, "_focused_slib_isbn", lambda: 123)
    monkeypatch.setattr(scanner, "_window_text", lambda _hwnd: "9789836276964")
    backend._seen_focus = 123
    backend._last_value = "9789836276964"
    backend._stable_value = "9789836276964"
    backend._stable_since = time.monotonic() - 1.0

    backend._poll_once()

    assert routed == ["9789836276964"]
    assert backend._pending == (123, "9789836276964")


@pytest.mark.skipif(os.name != "nt", reason="Windows control polling behavior")
def test_windows_backend_acknowledge_is_fail_open_if_field_changed(monkeypatch):
    statuses: list[str] = []
    backend = scanner._WindowsScannerBackend(
        is_enabled=lambda: True,
        on_scan=lambda _isbn: None,
        on_status=statuses.append,
    )
    backend._pending = (123, "9789836276964")
    monkeypatch.setattr(scanner.user32, "IsWindow", lambda _hwnd: 1)
    monkeypatch.setattr(scanner, "_window_text", lambda _hwnd: "9789836276965")

    assert backend.acknowledge("9789836276964") is False
    assert any("fail-open" in message for message in statuses)
