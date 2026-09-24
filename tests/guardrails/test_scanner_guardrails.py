from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCANNER = ROOT / "src" / "slib_assistant" / "scanner.py"


def test_scanner_router_has_no_coordinate_or_keyboard_injection_path():
    text = SCANNER.read_text(encoding="utf-8").casefold()
    forbidden = (
        "setcursorpos",
        "mouse_event",
        "sendinput",
        "keybd_event",
    )
    assert all(token not in text for token in forbidden)


def test_scanner_router_is_fail_open_before_suppressing_terminator():
    text = SCANNER.read_text(encoding="utf-8")
    assert "Fail-open" in text
    assert "_restore_original" in text
    assert "return 1" in text
