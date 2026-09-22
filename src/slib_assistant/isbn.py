from __future__ import annotations

import re
from dataclasses import dataclass


class ISBNError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class NormalizedISBN:
    isbn13: str
    isbn10: str | None


def _clean(value: str) -> str:
    return re.sub(r"[^0-9Xx]", "", value or "").upper()


def is_valid_isbn10(value: str) -> bool:
    digits = _clean(value)
    if len(digits) != 10 or not re.fullmatch(r"\d{9}[\dX]", digits):
        return False
    total = sum(
        (10 - index) * (10 if char == "X" else int(char))
        for index, char in enumerate(digits)
    )
    return total % 11 == 0


def is_valid_isbn13(value: str) -> bool:
    digits = _clean(value)
    if len(digits) != 13 or not digits.isdigit():
        return False
    total = sum(
        int(char) * (1 if index % 2 == 0 else 3)
        for index, char in enumerate(digits[:12])
    )
    check = (10 - total % 10) % 10
    return check == int(digits[-1])


def isbn10_to_isbn13(value: str) -> str:
    digits = _clean(value)
    if not is_valid_isbn10(digits):
        raise ISBNError("ISBN-10 checksum tidak sah.")
    body = "978" + digits[:9]
    total = sum(
        int(char) * (1 if index % 2 == 0 else 3)
        for index, char in enumerate(body)
    )
    return body + str((10 - total % 10) % 10)


def isbn13_to_isbn10(value: str) -> str | None:
    digits = _clean(value)
    if not is_valid_isbn13(digits) or not digits.startswith("978"):
        return None
    body = digits[3:12]
    total = sum((10 - index) * int(char) for index, char in enumerate(body))
    check = (11 - total % 11) % 11
    return body + ("X" if check == 10 else str(check))


def normalize_isbn(value: str) -> NormalizedISBN:
    digits = _clean((value or "").strip())
    if len(digits) == 10:
        if not is_valid_isbn10(digits):
            raise ISBNError("ISBN-10 checksum tidak sah.")
        return NormalizedISBN(isbn10_to_isbn13(digits), digits)
    if len(digits) == 13:
        if not is_valid_isbn13(digits):
            raise ISBNError("ISBN-13 checksum tidak sah.")
        return NormalizedISBN(digits, isbn13_to_isbn10(digits))
    raise ISBNError("Barcode bukan ISBN-10 atau ISBN-13 yang sah.")
