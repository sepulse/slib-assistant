from __future__ import annotations

import os
import re
import threading
import time
from collections.abc import Callable

from slib_assistant.isbn import is_valid_isbn10, is_valid_isbn13


SCAN_MAX_SECONDS = 2.0
SLIB_ISBN_CONTROL_ID = 59
SLIB_ISBN_CLASS = "ThunderRT6TextBox"


def clean_scan(value: str) -> str:
    """Keep only ISBN-significant characters from a scanner sequence."""
    return re.sub(r"[^0-9Xx]", "", value or "").upper()


def valid_scanned_isbn(value: str, duration_seconds: float) -> str | None:
    """Return a normalized ISBN when a sequence looks like a barcode scan."""
    candidate = clean_scan(value)
    if duration_seconds < 0 or duration_seconds > SCAN_MAX_SECONDS:
        return None
    if len(candidate) == 10 and is_valid_isbn10(candidate):
        return candidate
    if len(candidate) == 13 and is_valid_isbn13(candidate):
        return candidate
    return None


def appended_scan_matches(current: str, original: str, scanned: str) -> bool:
    """Verify S-Lib still contains exactly the original value plus this scan."""
    if not current.startswith(original):
        return False
    return clean_scan(current[len(original) :]) == clean_scan(scanned)


class ScannerRouter:
    """Observe scanner input in S-Lib and route a confirmed ISBN internally.

    The important safety property is fail-open: number keys are never blocked.
    S-Lib receives the barcode normally while it is being scanned. Only the
    terminating Enter/Tab is suppressed, and only after we have successfully
    restored the S-Lib ISBN field to its exact pre-scan value. If restoration
    fails, the terminator is allowed through and the barcode remains in S-Lib.

    The router runs inside S-Lib Assistant, so a successful scan is delivered
    directly to the application's callback. It does not click coordinates,
    synthesize keyboard input, or inject anything into the S-Lib process.
    """

    def __init__(
        self,
        on_scan: Callable[[str], None],
        on_status: Callable[[str], None] | None = None,
    ) -> None:
        self._on_scan = on_scan
        self._on_status = on_status or (lambda _message: None)
        self._enabled = True
        self._lock = threading.Lock()
        self._backend: _WindowsScannerBackend | None = None

    @property
    def supported(self) -> bool:
        return os.name == "nt"

    def set_enabled(self, enabled: bool) -> None:
        with self._lock:
            self._enabled = bool(enabled)

    def is_enabled(self) -> bool:
        with self._lock:
            return self._enabled

    def start(self) -> bool:
        if not self.supported:
            self._on_status("Scanner Mode hanya tersedia pada Windows.")
            return False
        if self._backend is not None:
            return True
        backend = _WindowsScannerBackend(
            is_enabled=self.is_enabled,
            on_scan=self._on_scan,
            on_status=self._on_status,
        )
        if not backend.start():
            return False
        self._backend = backend
        return True

    def stop(self) -> None:
        backend = self._backend
        self._backend = None
        if backend is not None:
            backend.stop()

    def acknowledge(self, isbn: str) -> bool:
        """Confirm Assistant received an ISBN, then clear that exact value in S-Lib.

        Until this acknowledgement succeeds, Scanner Mode leaves the barcode in
        S-Lib. This makes routing fail-open instead of silently consuming input.
        """
        backend = self._backend
        if backend is None:
            return False
        return backend.acknowledge(isbn)


if os.name == "nt":
    import ctypes
    from ctypes import wintypes

    WM_SETTEXT = 0x000C
    SMTO_ABORTIFHUNG = 0x0002
    ULONG_PTR = wintypes.WPARAM

    class GUITHREADINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.DWORD),
            ("flags", wintypes.DWORD),
            ("hwndActive", wintypes.HWND),
            ("hwndFocus", wintypes.HWND),
            ("hwndCapture", wintypes.HWND),
            ("hwndMenuOwner", wintypes.HWND),
            ("hwndMoveSize", wintypes.HWND),
            ("hwndCaret", wintypes.HWND),
            ("rcCaret", wintypes.RECT),
        ]

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.GetWindowThreadProcessId.argtypes = [
        wintypes.HWND,
        ctypes.POINTER(wintypes.DWORD),
    ]
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    user32.GetGUIThreadInfo.argtypes = [
        wintypes.DWORD,
        ctypes.POINTER(GUITHREADINFO),
    ]
    user32.GetGUIThreadInfo.restype = wintypes.BOOL
    user32.GetDlgCtrlID.argtypes = [wintypes.HWND]
    user32.GetDlgCtrlID.restype = ctypes.c_int
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextLengthW.restype = ctypes.c_int
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowTextW.restype = ctypes.c_int
    user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetClassNameW.restype = ctypes.c_int
    user32.IsWindow.argtypes = [wintypes.HWND]
    user32.IsWindow.restype = wintypes.BOOL
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.restype = wintypes.BOOL
    user32.SendMessageTimeoutW.argtypes = [
        wintypes.HWND,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM,
        wintypes.UINT,
        wintypes.UINT,
        ctypes.POINTER(ULONG_PTR),
    ]
    user32.SendMessageTimeoutW.restype = wintypes.LPARAM


    def _window_text(hwnd: int) -> str:
        length = user32.GetWindowTextLengthW(hwnd)
        buffer = ctypes.create_unicode_buffer(max(1, length + 1))
        user32.GetWindowTextW(hwnd, buffer, len(buffer))
        return buffer.value


    def _class_name(hwnd: int) -> str:
        buffer = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buffer, len(buffer))
        return buffer.value


    def _isbn_from_field(value: str) -> str | None:
        candidate = clean_scan(value)
        if len(candidate) == 10 and is_valid_isbn10(candidate):
            return candidate
        if len(candidate) == 13 and is_valid_isbn13(candidate):
            return candidate
        return None


    class _WindowsScannerBackend:
        """Poll the real S-Lib ISBN textbox; never intercept keyboard input."""

        def __init__(
            self,
            is_enabled: Callable[[], bool],
            on_scan: Callable[[str], None],
            on_status: Callable[[str], None],
        ) -> None:
            self._is_enabled = is_enabled
            self._on_scan = on_scan
            self._on_status = on_status
            self._thread: threading.Thread | None = None
            self._stop = threading.Event()
            self._pending: tuple[int, str] | None = None
            self._seen_focus: int | None = None
            self._last_value = ""
            self._stable_value = ""
            self._stable_since = 0.0
            self._last_status = ""

        def start(self) -> bool:
            self._thread = threading.Thread(
                target=self._run,
                name="SLibScannerMonitor",
                daemon=True,
            )
            self._thread.start()
            self._emit_status(
                "Scanner Mode aktif — menunggu medan ISBN/ISSN S-Lib."
            )
            return True

        def stop(self) -> None:
            self._stop.set()
            thread = self._thread
            if thread is not None and thread.is_alive():
                thread.join(timeout=1.0)

        def acknowledge(self, isbn: str) -> bool:
            pending = self._pending
            if pending is None:
                return False
            hwnd, expected = pending
            if expected != isbn or not user32.IsWindow(hwnd):
                return False
            current = _window_text(hwnd)
            if clean_scan(current) != clean_scan(expected):
                self._emit_status(
                    "Scanner Mode fail-open: ISBN dikekalkan di S-Lib kerana "
                    "nilai medan telah berubah sebelum pengesahan."
                )
                self._pending = None
                return False
            empty = ctypes.create_unicode_buffer("")
            result = ULONG_PTR()
            sent = user32.SendMessageTimeoutW(
                hwnd,
                WM_SETTEXT,
                0,
                ctypes.cast(empty, ctypes.c_void_p).value,
                SMTO_ABORTIFHUNG,
                300,
                ctypes.byref(result),
            )
            if not sent or _window_text(hwnd) != "":
                self._emit_status(
                    "Scanner Mode fail-open: ISBN sudah diterima Assistant tetapi "
                    "tidak dapat dibersihkan dari S-Lib."
                )
                self._pending = None
                return False
            self._pending = None
            self._seen_focus = hwnd
            self._last_value = ""
            self._stable_value = ""
            self._stable_since = time.monotonic()
            self._emit_status("Scanner Mode: ISBN diterima oleh Assistant.")
            return True

        def _emit_status(self, message: str) -> None:
            if message == self._last_status:
                return
            self._last_status = message
            self._on_status(message)

        def _focused_slib_isbn(self) -> int | None:
            top = user32.GetForegroundWindow()
            if not top:
                return None
            title = _window_text(top).casefold()
            if "s-lib v1001" not in title and "kemaskini bahan" not in title:
                return None
            thread_id = user32.GetWindowThreadProcessId(top, None)
            if not thread_id:
                return None
            info = GUITHREADINFO(cbSize=ctypes.sizeof(GUITHREADINFO))
            if not user32.GetGUIThreadInfo(thread_id, ctypes.byref(info)):
                return None
            focus = info.hwndFocus
            if not focus or not user32.IsWindowVisible(focus):
                return None
            if user32.GetDlgCtrlID(focus) != SLIB_ISBN_CONTROL_ID:
                return None
            if _class_name(focus).casefold() != SLIB_ISBN_CLASS.casefold():
                return None
            return int(focus)

        def _run(self) -> None:
            while not self._stop.wait(0.03):
                if not self._is_enabled() or self._pending is not None:
                    continue
                self._poll_once()

        def _poll_once(self) -> None:
            focus = self._focused_slib_isbn()
            if focus is None:
                return
            if focus != self._seen_focus:
                self._seen_focus = focus
                self._last_value = _window_text(focus)
                self._stable_value = self._last_value
                self._stable_since = time.monotonic()
                self._emit_status("Scanner Mode: medan ISBN/ISSN S-Lib dikesan.")
                return

            value = _window_text(focus)
            if value != self._last_value:
                self._last_value = value
                self._stable_value = value
                self._stable_since = time.monotonic()
                return

            if not value or time.monotonic() - self._stable_since < 0.09:
                return
            isbn = _isbn_from_field(value)
            if isbn is None:
                return
            # Only route when the field consists solely of the scanned ISBN.
            # If staff had pre-existing content, leave it untouched (fail-open).
            if clean_scan(value) != isbn:
                return
            self._pending = (focus, isbn)
            self._emit_status(f"Scanner Mode: ISBN dikesan {isbn}.")
            self._on_scan(isbn)


else:

    class _WindowsScannerBackend:  # pragma: no cover - Windows-only implementation
        def __init__(self, **_kwargs: object) -> None:
            pass

        def start(self) -> bool:
            return False

        def stop(self) -> None:
            return None

        def acknowledge(self, _isbn: str) -> bool:
            return False
