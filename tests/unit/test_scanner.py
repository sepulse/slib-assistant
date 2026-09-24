import ctypes
import os

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


@pytest.mark.skipif(os.name != "nt", reason="Windows keyboard hook behavior")
def test_windows_backend_suppresses_only_terminator_after_safe_restore(monkeypatch):
    routed: list[str] = []
    backend = scanner._WindowsScannerBackend(
        is_enabled=lambda: True,
        on_scan=routed.append,
        on_status=lambda _message: None,
    )
    monkeypatch.setattr(backend, "_focused_slib_isbn", lambda: 123)
    monkeypatch.setattr(backend, "_restore_original", lambda *_args: True)
    monkeypatch.setattr(scanner, "_window_text", lambda _hwnd: "")

    def key(vk: int) -> int:
        event = scanner.KBDLLHOOKSTRUCT(vkCode=vk)
        return backend._keyboard_proc(
            0,
            scanner.WM_KEYDOWN,
            ctypes.addressof(event),
        )

    for digit in "9789836276964":
        # Digits are fail-open and continue to S-Lib.
        assert key(ord(digit)) == 0
    # Only the scanner terminator is swallowed after safe restoration.
    assert key(scanner.VK_RETURN) == 1
    assert routed == ["9789836276964"]


@pytest.mark.skipif(os.name != "nt", reason="Windows keyboard hook behavior")
def test_windows_backend_fail_open_when_restore_cannot_be_verified(monkeypatch):
    routed: list[str] = []
    statuses: list[str] = []
    backend = scanner._WindowsScannerBackend(
        is_enabled=lambda: True,
        on_scan=routed.append,
        on_status=statuses.append,
    )
    monkeypatch.setattr(backend, "_focused_slib_isbn", lambda: 123)
    monkeypatch.setattr(backend, "_restore_original", lambda *_args: False)
    monkeypatch.setattr(scanner, "_window_text", lambda _hwnd: "")

    def key(vk: int) -> int:
        event = scanner.KBDLLHOOKSTRUCT(vkCode=vk)
        return backend._keyboard_proc(
            0,
            scanner.WM_KEYDOWN,
            ctypes.addressof(event),
        )

    for digit in "9789836276964":
        assert key(ord(digit)) == 0
    # Enter is also fail-open when the S-Lib field cannot be safely restored.
    assert key(scanner.VK_RETURN) == 0
    assert routed == []
    assert any("fail-open" in message for message in statuses)
