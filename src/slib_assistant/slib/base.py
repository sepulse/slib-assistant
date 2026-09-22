from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SLibCapabilities:
    detected: bool = False
    verified_new_record_form: bool = False
    text_fields: set[str] = field(default_factory=set)
    option_fields: set[str] = field(default_factory=set)
    office_mapping_confirmed: bool = False


@dataclass(slots=True)
class FieldFillResult:
    field: str
    attempted: bool
    success: bool
    message: str = ""


class SLibAdapter(ABC):
    @abstractmethod
    def detect(self) -> bool: raise NotImplementedError

    @abstractmethod
    def verify_new_record_form(self) -> bool: raise NotImplementedError

    @abstractmethod
    def get_capabilities(self) -> SLibCapabilities: raise NotImplementedError

    @abstractmethod
    def fill_text(self, field: str, value: str) -> FieldFillResult: raise NotImplementedError

    @abstractmethod
    def select_option(self, field: str, value: str) -> FieldFillResult: raise NotImplementedError

    def fill_record(self, mapped_record: dict[str, Any]) -> list[FieldFillResult]:
        if not self.verify_new_record_form():
            raise RuntimeError("S-Lib Data Baru form tidak dapat disahkan.")
        results: list[FieldFillResult] = []
        for field_name, value in mapped_record.items():
            if value in (None, "", []):
                results.append(FieldFillResult(field_name, False, True, "blank skipped"))
                continue
            if isinstance(value, dict) and value.get("kind") == "option":
                results.append(self.select_option(field_name, str(value.get("value", ""))))
            else:
                results.append(self.fill_text(field_name, str(value)))
        return results

    @abstractmethod
    def abort(self) -> None: raise NotImplementedError
