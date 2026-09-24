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
        "setwindowshookex",
        "callnexthookex",
    )
    assert all(token not in text for token in forbidden)


def test_scanner_router_is_acknowledged_fail_open_polling():
    text = SCANNER.read_text(encoding="utf-8")
    assert "def acknowledge" in text
    assert "_poll_once" in text
    assert "WM_SETTEXT" in text
    assert "fail-open" in text.casefold()
