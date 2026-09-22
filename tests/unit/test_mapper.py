from slib_assistant.models import BookMetadata
from slib_assistant.slib.mapper import map_book_to_slib


def test_mapper_never_invents_call_number_or_price():
    mapped = map_book_to_slib(
        BookMetadata(
            isbn13="9789836276964",
            title="Test",
            authors=["A", "B", "C", "D"],
            price="99.00",
        )
    )
    assert mapped["author_1"] == "A"
    assert mapped["author_3"] == "C"
    assert "call_number" not in mapped
    assert "price" not in mapped
