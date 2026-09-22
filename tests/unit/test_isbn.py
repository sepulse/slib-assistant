import pytest

from slib_assistant.isbn import ISBNError, isbn10_to_isbn13, normalize_isbn


def test_isbn13_normalizes_scanner_format():
    result = normalize_isbn("978-983-627-696-4\r\n")
    assert result.isbn13 == "9789836276964"


def test_isbn10_converts_to_isbn13():
    result = normalize_isbn("0306406152")
    assert result.isbn13 == isbn10_to_isbn13("0306406152")
    assert result.isbn13 == "9780306406157"
    assert result.isbn10 == "0306406152"


def test_invalid_checksum_rejected():
    with pytest.raises(ISBNError):
        normalize_isbn("9789836276965")
