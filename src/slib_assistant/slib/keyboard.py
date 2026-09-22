from __future__ import annotations

from slib_assistant.slib.base import FieldFillResult, SLibAdapter, SLibCapabilities


class KeyboardFallbackAdapter(SLibAdapter):
    def __init__(self, tab_order: list[str] | None = None):
        self.tab_order = tab_order or []
        self._aborted = False

    def detect(self) -> bool: return bool(self.tab_order)
    def verify_new_record_form(self) -> bool: return bool(self.tab_order) and not self._aborted
    def get_capabilities(self) -> SLibCapabilities:
        return SLibCapabilities(detected=self.detect(), verified_new_record_form=self.verify_new_record_form(), text_fields=set(self.tab_order), office_mapping_confirmed=bool(self.tab_order))
    def fill_text(self, field: str, value: str) -> FieldFillResult:
        return FieldFillResult(field, False, False, "Keyboard fallback pending office-confirmed tab order.")
    def select_option(self, field: str, value: str) -> FieldFillResult:
        return self.fill_text(field, value)
    def abort(self) -> None:
        self._aborted = True
