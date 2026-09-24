from __future__ import annotations

import logging
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


if os.name == "nt":
    import ctypes
    from ctypes import wintypes

    WH_KEYBOARD_LL = 13
    WM_KEYDOWN = 0x0100
    WM_SYSKEYDOWN = 0x0104
    WM_QUIT = 0x0012
    WM_SETTEXT = 0x000C
    VK_RETURN = 0x0D
    VK_TAB = 0x09
    LLKHF_INJECTED = 0x10
    SMTO_ABORTIFHUNG = 0x0002

    LRESULT = ctypes.c_ssize_t
    ULONG_PTR = wintypes.WPARAM

    class KBDLLHOOKSTRUCT(ctypes.Structure):
        _fields_ = [
            ("vkCode", wintypes.DWORD),
            ("scanCode", wintypes.DWORD),
            ("flags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ULONG_PTR),
        ]

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

    HOOKPROC = ctypes.WINFUNCTYPE(
        LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM
    )

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    user32.SetWindowsHookExW.argtypes = [
        ctypes.c_int,
        HOOKPROC,
        wintypes.HINSTANCE,
        wintypes.DWORD,
    ]
    user32.SetWindowsHookExW.restype = wintypes.HHOOK
    user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
    user32.UnhookWindowsHookEx.restype = wintypes.BOOL
    user32.CallNextHookEx.argtypes = [
        wintypes.HHOOK,
        ctypes.c_int,
        wintypes.WPARAM,
        wintypes.LPARAM,
    ]
    user32.CallNextHookEx.restype = LRESULT
    user32.GetMessageW.argtypes = [
        ctypes.POINTER(wintypes.MSG),
        wintypes.HWND,
        wintypes.UINT,
        wintypes.UINT,
    ]
    user32.GetMessageW.restype = wintypes.BOOL
    user32.PostThreadMessageW.argtypes = [
        wintypes.DWORD,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM,
    ]
    user32.PostThreadMessageW.restype = wintypes.BOOL
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
    user32.IsChild.argtypes = [wintypes.HWND, wintypes.HWND]
    user32.IsChild.restype = wintypes.BOOL
    user32.GetDlgCtrlID.argtypes = [wintypes.HWND]
    user32.GetDlgCtrlID.restype = ctypes.c_int
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextLengthW.restype = ctypes.c_int
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowTextW.restype = ctypes.c_int
    user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetClassNameW.restype = ctypes.c_int
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
    kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
    kernel32.GetModuleHandleW.restype = wintypes.HMODULE
    kernel32.GetCurrentThreadId.restype = wintypes.DWORD


    def _window_text(hwnd: int) -> str:
        length = user32.GetWindowTextLengthW(hwnd)
        buffer = ctypes.create_unicode_buffer(max(1, length + 1))
        user32.GetWindowTextW(hwnd, buffer, len(buffer))
        return buffer.value


    def _class_name(hwnd: int) -> str:
        buffer = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buffer, len(buffer))
        return buffer.value


    def _candidate_char(vk: int) -> str | None:
        if 0x30 <= vk <= 0x39:
            return chr(ord("0") + vk - 0x30)
        if 0x60 <= vk <= 0x69:
            return chr(ord("0") + vk - 0x60)
        if vk == 0x58:
            return "X"
        if vk in (0xBD, 0x6D):
            return "-"
        return None


    class _WindowsScannerBackend:
        def __init__(
            self,
            is_enabled: Callable[[], bool],
            on_scan: Callable[[str], None],
            on_status: Callable[[str], None],
        ) -> None:
            self._is_enabled = is_enabled
            self._on_scan = on_scan
            self._on_status = on_status
            self._hook: int | None = None
            self._thread: threading.Thread | None = None
            self._thread_id: int | None = None
            self._ready = threading.Event()
            self._start_ok = False
            self._hook_proc = HOOKPROC(self._keyboard_proc)
            self._buffer: list[str] = []
            self._focus: int | None = None
            self._original = ""
            self._started_at = 0.0

        def start(self) -> bool:
            self._thread = threading.Thread(
                target=self._run,
                name="SLibScannerRouter",
                daemon=True,
            )
            self._thread.start()
            if not self._ready.wait(timeout=2.0):
                self._on_status("Scanner Mode gagal dimulakan (timeout).")
                return False
            return self._start_ok

        def stop(self) -> None:
            if self._thread_id is not None:
                user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
            thread = self._thread
            if thread is not None and thread.is_alive():
                thread.join(timeout=1.0)

        def _run(self) -> None:
            self._thread_id = int(kernel32.GetCurrentThreadId())
            module = kernel32.GetModuleHandleW(None)
            hook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, self._hook_proc, module, 0)
            if not hook:
                error = ctypes.get_last_error()
                self._on_status(f"Scanner Mode gagal memasang hook Windows ({error}).")
                self._ready.set()
                return
            self._hook = int(hook)
            self._start_ok = True
            self._ready.set()
            self._on_status("Scanner Mode aktif — scan ISBN pada medan ISBN/ISSN S-Lib.")
            try:
                message = wintypes.MSG()
                while user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
                    pass
            finally:
                user32.UnhookWindowsHookEx(hook)
                self._hook = None

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
            if not focus:
                return None
            if focus != top and not user32.IsChild(top, focus):
                return None
            if user32.GetDlgCtrlID(focus) != SLIB_ISBN_CONTROL_ID:
                return None
            if _class_name(focus).casefold() != SLIB_ISBN_CLASS.casefold():
                return None
            return int(focus)

        def _reset(self) -> None:
            self._buffer.clear()
            self._focus = None
            self._original = ""
            self._started_at = 0.0

        def _restore_original(self, focus: int, original: str, scanned: str) -> bool:
            current = _window_text(focus)
            if not appended_scan_matches(current, original, scanned):
                return False
            value = ctypes.create_unicode_buffer(original)
            result = ULONG_PTR()
            sent = user32.SendMessageTimeoutW(
                focus,
                WM_SETTEXT,
                0,
                ctypes.cast(value, ctypes.c_void_p).value,
                SMTO_ABORTIFHUNG,
                300,
                ctypes.byref(result),
            )
            return bool(sent) and _window_text(focus) == original

        def _keyboard_proc(self, n_code: int, w_param: int, l_param: int) -> int:
            if n_code < 0 or w_param not in (WM_KEYDOWN, WM_SYSKEYDOWN):
                return user32.CallNextHookEx(self._hook, n_code, w_param, l_param)
            event = ctypes.cast(l_param, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            if event.flags & LLKHF_INJECTED:
                return user32.CallNextHookEx(self._hook, n_code, w_param, l_param)
            if not self._is_enabled():
                self._reset()
                return user32.CallNextHookEx(self._hook, n_code, w_param, l_param)

            focus = self._focused_slib_isbn()
            vk = int(event.vkCode)
            char = _candidate_char(vk)

            if char is not None and focus is not None:
                now = time.monotonic()
                if not self._buffer or self._focus != focus:
                    self._reset()
                    self._focus = focus
                    self._original = _window_text(focus)
                    self._started_at = now
                self._buffer.append(char)
                # Fail-open: the actual character is always delivered to S-Lib.
                return user32.CallNextHookEx(self._hook, n_code, w_param, l_param)

            if vk in (VK_RETURN, VK_TAB) and self._buffer:
                scanned = "".join(self._buffer)
                duration = time.monotonic() - self._started_at
                buffered_focus = self._focus
                original = self._original
                self._reset()
                normalized = valid_scanned_isbn(scanned, duration)
                if (
                    normalized is not None
                    and focus is not None
                    and buffered_focus == focus
                    and self._restore_original(focus, original, scanned)
                ):
                    try:
                        self._on_scan(normalized)
                    except Exception:
                        logging.exception("Scanner callback failed")
                    # Only now is the terminator suppressed. The barcode itself
                    # was already accepted by S-Lib and safely rolled back.
                    return 1
                if normalized is not None:
                    self._on_status(
                        "Scanner Mode fail-open: ISBN dikekalkan di S-Lib kerana "
                        "medan tidak dapat dipulihkan dengan pasti."
                    )
                # Any uncertainty is fail-open: keep the barcode in S-Lib and
                # let Enter/Tab continue normally.
                return user32.CallNextHookEx(self._hook, n_code, w_param, l_param)

            if self._buffer:
                self._reset()
            return user32.CallNextHookEx(self._hook, n_code, w_param, l_param)


else:

    class _WindowsScannerBackend:  # pragma: no cover - Windows-only implementation
        def __init__(self, **_kwargs: object) -> None:
            pass

        def start(self) -> bool:
            return False

        def stop(self) -> None:
            return None
