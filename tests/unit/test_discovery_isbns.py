from slib_assistant.isbn import normalize_isbn


def test_documented_discovery_samples_are_valid():
    samples = [
        "9789836276964",
        "9780786849567",
        "9781921344503",
        "9789836294845",
        "9789676126139",
    ]
    assert [normalize_isbn(value).isbn13 for value in samples] == samples
