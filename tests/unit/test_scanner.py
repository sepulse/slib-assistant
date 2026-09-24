import os
import time

import pytest

import slib_assistant.scanner as scanner
from slib_assistant.scanner import DeviceBuffer, clean_scan, valid_scanned_isbn


def test_clean_scan_accepts_common_barcode_formatting():
    assert clean_scan("978-983-62-7696-4\r\n") == "9789836276964"


def test_valid_fast_isbn13():
    assert valid_scanned_isbn("9789836276964", 0.15) == "9789836276964"


def test_slow_typing_is_not_treated_as_scanner():
    assert valid_scanned_isbn("9789836276964", 3.0) is None


def test_invalid_checksum_is_not_routed():
    assert valid_scanned_isbn("9789836276965", 0.1) is None


def test_device_buffer_finalizes_valid_isbn_after_idle():
    state = DeviceBuffer()
    started = 100.0
    for index, char in enumerate("9789836276964"):
        state.append(char, started + index * 0.01)
    assert state.isbn(started + 0.30, require_idle=True) == "9789836276964"


def test_device_buffer_rejects_slow_human_entry():
    state = DeviceBuffer()
    for index, char in enumerate("9789836276964"):
        state.append(char, index * 0.25)
    assert state.isbn(3.2, require_idle=True) is None


@pytest.mark.skipif(os.name != "nt", reason="Windows Raw Input behavior")
def test_windows_raw_input_backend_can_start_and_stop():
    statuses: list[str] = []
    backend = scanner._WindowsScannerBackend(
        is_enabled=lambda: True,
        on_scan=lambda _isbn: None,
        on_status=statuses.append,
    )
    assert backend.start() is True
    assert any("Raw Input sedia" in message for message in statuses)
    backend.stop()
