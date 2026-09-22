from slib_assistant.models import Confidence, ProviderRecord
from slib_assistant.resolver import resolve_records


def record(provider, **data):
    return ProviderRecord(provider=provider, isbn13="9789836276964", data=data)


def test_consensus_has_high_confidence_and_provenance():
    result = resolve_records(
        "9789836276964",
        [record("a", title="Buku A"), record("b", title="Buku A")],
    )
    assert result.title == "Buku A"
    assert result.field_confidence["title"] == Confidence.HIGH
    assert result.field_provenance["title"] == ["a", "b"]


def test_conflict_visible_to_operator():
    result = resolve_records(
        "9789836276964",
        [record("a", publication_year=2020), record("b", publication_year=2021)],
    )
    assert result.field_confidence["publication_year"] == Confidence.REVIEW
    assert result.conflicts[0].field == "publication_year"


def test_missing_stays_missing():
    result = resolve_records("9789836276964", [])
    assert result.ddc is None
    assert result.field_confidence["ddc"] == Confidence.MISSING
