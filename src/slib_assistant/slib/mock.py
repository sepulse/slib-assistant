from __future__ import annotations

from slib_assistant.slib.base import FieldFillResult, SLibAdapter, SLibCapabilities


class MockSLibAdapter(SLibAdapter):
    def __init__(self, detected: bool = True, correct_form: bool = True):
        self.detected = detected
        self.correct_form = correct_form
        self.aborted = False
        self.values: dict[str, str] = {}

    def detect(self) -> bool:
        return self.detected

    def verify_new_record_form(self) -> bool:
        return self.detected and self.correct_form and not self.aborted

    def get_capabilities(self) -> SLibCapabilities:
        return SLibCapabilities(detected=self.detected, verified_new_record_form=self.verify_new_record_form(), office_mapping_confirmed=False)

    def fill_text(self, field: str, value: str) -> FieldFillResult:
        if not self.verify_new_record_form():
            return FieldFillResult(field, True, False, "wrong window or aborted")
        if not value:
            return FieldFillResult(field, False, True, "blank skipped")
        self.values[field] = value
        return FieldFillResult(field, True, True)

    def select_option(self, field: str, value: str) -> FieldFillResult:
        return self.fill_text(field, value)

    def abort(self) -> None:
        self.aborted = True
