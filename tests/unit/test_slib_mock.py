import pytest

from slib_assistant.slib.mock import MockSLibAdapter


def test_wrong_window_blocks_fill():
    adapter = MockSLibAdapter(correct_form=False)
    with pytest.raises(RuntimeError):
        adapter.fill_record({"title": "Test"})


def test_blank_does_not_overwrite():
    adapter = MockSLibAdapter()
    adapter.values["publisher"] = "Existing"
    result = adapter.fill_record({"publisher": ""})
    assert adapter.values["publisher"] == "Existing"
    assert result[0].attempted is False


def test_abort_blocks_mutation():
    adapter = MockSLibAdapter()
    adapter.abort()
    with pytest.raises(RuntimeError):
        adapter.fill_record({"title": "Test"})


def test_no_save_surface_exists():
    adapter = MockSLibAdapter()
    assert not hasattr(adapter, "save")
