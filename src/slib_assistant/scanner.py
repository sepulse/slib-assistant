from __future__ import annotations

import os
import re
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field

from slib_assistant.isbn import is_valid_isbn10, is_valid_isbn13


SCAN_MAX_SECONDS = 2.0
SCAN_IDLE_SECONDS = 0.15


def clean_scan(value: str) -> str:
    """Keep only ISBN-significant characters from a scanner sequence."""
    return re.sub(r"[^0-9Xx]", "", value or "").upper()


def valid_scanned_isbn(value: str, duration_seconds: float) -> str | None:
    """Return an ISBN only when checksum and scanner-like timing both pass."""
    candidate = clean_scan(value)
    if duration_seconds < 0 or duration_seconds > SCAN_MAX_SECONDS:
        return None
    if len(candidate) == 10 and is_valid_isbn10(candidate):
        return candidate
    if len(candidate) == 13 and is_valid_isbn13(candidate):
        return candidate
    return None


@dataclass(slots=True)
class DeviceBuffer:
    chars: list[str] = field(default_factory=list)
    started_at: float = 0.0
    last_at: float = 0.0

    def reset(self) -> None:
        self.chars.clear()
        self.started_at = 0.0
        self.last_at = 0.0

    def append(self, char: str, now: float) -> None:
        if not self.chars:
            self.started_at = now
        self.last_at = now
        self.chars.append(char)

    def isbn(self, now: float, *, require_idle: bool) -> str | None:
        if not self.chars:
            return None
        if require_idle and now - self.last_at < SCAN_IDLE_SECONDS:
            return None
        return valid_scanned_isbn("".join(self.chars), now - self.started_at)


class ScannerRouter:
    """Observe HID keyboard scans using Windows Raw Input.

    The router never blocks or rewrites keyboard input. S-Lib receives the scan
    normally. In parallel, a valid fast ISBN seen while S-Lib is foreground is
    copied directly into S-Lib Assistant. This is deliberately fail-open: if
    Raw Input detection fails, normal S-Lib barcode entry remains unaffected.
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

    WM_INPUT = 0x00FF
    WM_TIMER = 0x0113
    WM_DESTROY = 0x0002
    WM_CLOSE = 0x0010
    WM_KEYDOWN = 0x0100
    WM_SYSKEYDOWN = 0x0104

    RIM_TYPEKEYBOARD = 1
    RID_INPUT = 0x10000003
    RIDEV_INPUTSINK = 0x00000100
    HID_USAGE_PAGE_GENERIC = 0x01
    HID_USAGE_GENERIC_KEYBOARD = 0x06

    VK_RETURN = 0x0D
    VK_TAB = 0x09
    VK_SHIFT = 0x10
    VK_CONTROL = 0x11
    VK_MENU = 0x12
    VK_CAPITAL = 0x14
    VK_NUMLOCK = 0x90

    LRESULT = ctypes.c_ssize_t
    ULONG_PTR = wintypes.WPARAM

    class RAWINPUTDEVICE(ctypes.Structure):
        _fields_ = [
            ("usUsagePage", wintypes.USHORT),
            ("usUsage", wintypes.USHORT),
            ("dwFlags", wintypes.DWORD),
            ("hwndTarget", wintypes.HWND),
        ]

    class RAWINPUTHEADER(ctypes.Structure):
        _fields_ = [
            ("dwType", wintypes.DWORD),
            ("dwSize", wintypes.DWORD),
            ("hDevice", wintypes.HANDLE),
            ("wParam", wintypes.WPARAM),
        ]

    class RAWKEYBOARD(ctypes.Structure):
        _fields_ = [
            ("MakeCode", wintypes.USHORT),
            ("Flags", wintypes.USHORT),
            ("Reserved", wintypes.USHORT),
            ("VKey", wintypes.USHORT),
            ("Message", wintypes.UINT),
            ("ExtraInformation", wintypes.ULONG),
        ]

    class RAWINPUTUNION(ctypes.Union):
        _fields_ = [("keyboard", RAWKEYBOARD)]

    class RAWINPUT(ctypes.Structure):
        _anonymous_ = ("data",)
        _fields_ = [("header", RAWINPUTHEADER), ("data", RAWINPUTUNION)]

    class WNDCLASSW(ctypes.Structure):
        _fields_ = [
            ("style", wintypes.UINT),
            ("lpfnWndProc", ctypes.c_void_p),
            ("cbClsExtra", ctypes.c_int),
            ("cbWndExtra", ctypes.c_int),
            ("hInstance", wintypes.HINSTANCE),
            ("hIcon", wintypes.HICON),
            ("hCursor", wintypes.HANDLE),
            ("hbrBackground", wintypes.HBRUSH),
            ("lpszMenuName", wintypes.LPCWSTR),
            ("lpszClassName", wintypes.LPCWSTR),
        ]

    WNDPROC = ctypes.WINFUNCTYPE(
        LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM
    )

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    user32.RegisterClassW.argtypes = [ctypes.POINTER(WNDCLASSW)]
    user32.RegisterClassW.restype = wintypes.ATOM
    user32.UnregisterClassW.argtypes = [wintypes.LPCWSTR, wintypes.HINSTANCE]
    user32.UnregisterClassW.restype = wintypes.BOOL
    user32.CreateWindowExW.argtypes = [
        wintypes.DWORD,
        wintypes.LPCWSTR,
        wintypes.LPCWSTR,
        wintypes.DWORD,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.HWND,
        wintypes.HMENU,
        wintypes.HINSTANCE,
        wintypes.LPVOID,
    ]
    user32.CreateWindowExW.restype = wintypes.HWND
    user32.DestroyWindow.argtypes = [wintypes.HWND]
    user32.DestroyWindow.restype = wintypes.BOOL
    user32.DefWindowProcW.argtypes = [
        wintypes.HWND,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM,
    ]
    user32.DefWindowProcW.restype = LRESULT
    user32.GetMessageW.argtypes = [
        ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT
    ]
    user32.GetMessageW.restype = wintypes.BOOL
    user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
    user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
    user32.PostMessageW.argtypes = [
        wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM
    ]
    user32.PostMessageW.restype = wintypes.BOOL
    user32.PostQuitMessage.argtypes = [ctypes.c_int]
    user32.SetTimer.argtypes = [
        wintypes.HWND, ULONG_PTR, wintypes.UINT, wintypes.LPVOID
    ]
    user32.SetTimer.restype = ULONG_PTR
    user32.KillTimer.argtypes = [wintypes.HWND, ULONG_PTR]
    user32.KillTimer.restype = wintypes.BOOL
    user32.RegisterRawInputDevices.argtypes = [
        ctypes.POINTER(RAWINPUTDEVICE), wintypes.UINT, wintypes.UINT
    ]
    user32.RegisterRawInputDevices.restype = wintypes.BOOL
    user32.GetRawInputData.argtypes = [
        wintypes.HANDLE,
        wintypes.UINT,
        wintypes.LPVOID,
        ctypes.POINTER(wintypes.UINT),
        wintypes.UINT,
    ]
    user32.GetRawInputData.restype = wintypes.UINT
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextLengthW.restype = ctypes.c_int
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowTextW.restype = ctypes.c_int
    kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
    kernel32.GetModuleHandleW.restype = wintypes.HMODULE

    TIMER_ID = 1


    def _window_text(hwnd: int) -> str:
        length = user32.GetWindowTextLengthW(hwnd)
        buffer = ctypes.create_unicode_buffer(max(1, length + 1))
        user32.GetWindowTextW(hwnd, buffer, len(buffer))
        return buffer.value


    def _foreground_is_slib() -> bool:
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return False
        title = _window_text(hwnd).casefold()
        return "s-lib v1001" in title or "kemaskini bahan" in title


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
            self._thread: threading.Thread | None = None
            self._ready = threading.Event()
            self._start_ok = False
            self._hwnd: int | None = None
            self._instance = kernel32.GetModuleHandleW(None)
            self._class_name = f"SLibAssistantRawInput_{os.getpid()}_{id(self)}"
            self._wndproc = WNDPROC(self._window_proc)
            self._buffers: dict[int, DeviceBuffer] = {}
            self._last_status = ""

        def start(self) -> bool:
            self._thread = threading.Thread(
                target=self._run, name="SLibRawInputReceiver", daemon=True
            )
            self._thread.start()
            if not self._ready.wait(timeout=2.0):
                self._emit_status("Scanner Mode gagal dimulakan (Raw Input timeout).")
                return False
            return self._start_ok

        def stop(self) -> None:
            hwnd = self._hwnd
            if hwnd:
                user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
            thread = self._thread
            if thread is not None and thread.is_alive():
                thread.join(timeout=1.0)

        def _emit_status(self, message: str) -> None:
            if message == self._last_status:
                return
            self._last_status = message
            self._on_status(message)

        def _run(self) -> None:
            wc = WNDCLASSW()
            wc.lpfnWndProc = ctypes.cast(self._wndproc, ctypes.c_void_p).value
            wc.hInstance = self._instance
            wc.lpszClassName = self._class_name
            if not user32.RegisterClassW(ctypes.byref(wc)):
                self._emit_status(
                    f"Scanner Mode gagal daftar Raw Input ({ctypes.get_last_error()})."
                )
                self._ready.set()
                return
            try:
                hwnd = user32.CreateWindowExW(
                    0,
                    self._class_name,
                    "SLibAssistantRawInput",
                    0,
                    0,
                    0,
                    0,
                    0,
                    None,
                    None,
                    self._instance,
                    None,
                )
                if not hwnd:
                    self._emit_status(
                        f"Scanner Mode gagal cipta Raw Input window ({ctypes.get_last_error()})."
                    )
                    self._ready.set()
                    return
                self._hwnd = int(hwnd)
                device = RAWINPUTDEVICE(
                    HID_USAGE_PAGE_GENERIC,
                    HID_USAGE_GENERIC_KEYBOARD,
                    RIDEV_INPUTSINK,
                    hwnd,
                )
                if not user32.RegisterRawInputDevices(
                    ctypes.byref(device), 1, ctypes.sizeof(RAWINPUTDEVICE)
                ):
                    self._emit_status(
                        f"Scanner Mode gagal daftar keyboard Raw Input ({ctypes.get_last_error()})."
                    )
                    self._ready.set()
                    user32.DestroyWindow(hwnd)
                    return
                user32.SetTimer(hwnd, TIMER_ID, 50, None)
                self._start_ok = True
                self._ready.set()
                self._emit_status(
                    "Scanner Mode aktif — Raw Input sedia. Scan ISBN dalam S-Lib."
                )
                message = wintypes.MSG()
                while user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
                    user32.TranslateMessage(ctypes.byref(message))
                    user32.DispatchMessageW(ctypes.byref(message))
            finally:
                self._hwnd = None
                user32.UnregisterClassW(self._class_name, self._instance)

        def _window_proc(self, hwnd: int, message: int, wparam: int, lparam: int) -> int:
            if message == WM_INPUT:
                self._handle_raw_input(lparam)
                return 0
            if message == WM_TIMER and wparam == TIMER_ID:
                self._flush_idle_buffers()
                return 0
            if message == WM_CLOSE:
                user32.KillTimer(hwnd, TIMER_ID)
                user32.DestroyWindow(hwnd)
                return 0
            if message == WM_DESTROY:
                user32.PostQuitMessage(0)
                return 0
            return user32.DefWindowProcW(hwnd, message, wparam, lparam)

        def _handle_raw_input(self, raw_handle: int) -> None:
            size = wintypes.UINT(0)
            header_size = ctypes.sizeof(RAWINPUTHEADER)
            result = user32.GetRawInputData(
                raw_handle, RID_INPUT, None, ctypes.byref(size), header_size
            )
            if result == 0xFFFFFFFF or size.value < ctypes.sizeof(RAWINPUT):
                return
            buffer = ctypes.create_string_buffer(size.value)
            result = user32.GetRawInputData(
                raw_handle, RID_INPUT, buffer, ctypes.byref(size), header_size
            )
            if result == 0xFFFFFFFF:
                return
            raw = ctypes.cast(buffer, ctypes.POINTER(RAWINPUT)).contents
            if raw.header.dwType != RIM_TYPEKEYBOARD:
                return
            keyboard = raw.keyboard
            if keyboard.Message not in (WM_KEYDOWN, WM_SYSKEYDOWN):
                return
            if not self._is_enabled() or not _foreground_is_slib():
                return
            device = int(ctypes.cast(raw.header.hDevice, ctypes.c_void_p).value or 0)
            state = self._buffers.setdefault(device, DeviceBuffer())
            now = time.monotonic()
            vk = int(keyboard.VKey)
            char = _candidate_char(vk)
            if char is not None:
                if state.chars and now - state.last_at > SCAN_IDLE_SECONDS * 3:
                    state.reset()
                state.append(char, now)
                return
            if vk in (VK_SHIFT, VK_CONTROL, VK_MENU, VK_CAPITAL, VK_NUMLOCK):
                return
            if vk in (VK_RETURN, VK_TAB):
                self._finalize(device, now, require_idle=False)
                return
            state.reset()

        def _flush_idle_buffers(self) -> None:
            if not self._is_enabled() or not _foreground_is_slib():
                return
            now = time.monotonic()
            for device in list(self._buffers):
                self._finalize(device, now, require_idle=True)

        def _finalize(self, device: int, now: float, *, require_idle: bool) -> None:
            state = self._buffers.get(device)
            if state is None:
                return
            isbn = state.isbn(now, require_idle=require_idle)
            if isbn is None:
                if require_idle and state.chars and now - state.last_at > SCAN_MAX_SECONDS:
                    state.reset()
                return
            state.reset()
            self._emit_status(f"Scanner Mode: ISBN dikesan {isbn}")
            self._on_scan(isbn)


else:

    class _WindowsScannerBackend:  # pragma: no cover
        def __init__(self, **_kwargs: object) -> None:
            pass

        def start(self) -> bool:
            return False

        def stop(self) -> None:
            return None
