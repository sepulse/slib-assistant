from __future__ import annotations

import re
from typing import Any

from slib_assistant.slib.base import FieldFillResult, SLibAdapter, SLibCapabilities


class UIASLibAdapter(SLibAdapter):
    def __init__(
        self,
        window_title: str,
        field_selectors: dict[str, dict[str, Any]] | None = None,
        backend: str = "uia",
    ):
        if backend not in {"uia", "win32"}:
            raise ValueError("backend mesti 'uia' atau 'win32'")
        self.window_title = window_title
        self.field_selectors = field_selectors or {}
        self.backend = backend
        self._window = None
        self._aborted = False

    def _desktop(self):
        try:
            from pywinauto import Desktop
        except ImportError as exc:
            raise RuntimeError("pywinauto belum dipasang.") from exc
        return Desktop(backend=self.backend)

    def detect(self) -> bool:
        try:
            self._window = self._desktop().window(title_re=".*" + re.escape(self.window_title) + ".*")
            return bool(self._window.exists(timeout=0.5))
        except Exception:
            self._window = None
            return False

    def verify_new_record_form(self) -> bool:
        if self._aborted or not self.field_selectors:
            return False
        if self._window is None and not self.detect():
            return False
        try:
            return self.window_title.casefold() in self._window.window_text().casefold()
        except Exception:
            return False

    def get_capabilities(self) -> SLibCapabilities:
        detected = self.detect()
        return SLibCapabilities(detected=detected, verified_new_record_form=self.verify_new_record_form(), text_fields=set(self.field_selectors), office_mapping_confirmed=bool(self.field_selectors))

    def _control(self, field: str):
        selector = self.field_selectors.get(field)
        if not selector:
            raise KeyError(f"Field mapping belum disahkan: {field}")
        return self._window.child_window(**selector)

    def fill_text(self, field: str, value: str) -> FieldFillResult:
        if not value:
            return FieldFillResult(field, False, True, "blank skipped")
        if not self.verify_new_record_form():
            return FieldFillResult(field, True, False, "window/form verification failed")
        try:
            self._control(field).set_edit_text(value)
            return FieldFillResult(field, True, True)
        except Exception as exc:
            return FieldFillResult(field, True, False, str(exc))

    def select_option(self, field: str, value: str) -> FieldFillResult:
        if not value:
            return FieldFillResult(field, False, True, "blank skipped")
        if not self.verify_new_record_form():
            return FieldFillResult(field, True, False, "window/form verification failed")
        try:
            self._control(field).select(value)
            return FieldFillResult(field, True, True)
        except Exception as exc:
            return FieldFillResult(field, True, False, str(exc))

    def abort(self) -> None:
        self._aborted = True
