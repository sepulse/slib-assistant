from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"


def source_text():
    return "\n".join(path.read_text(encoding="utf-8") for path in SRC.rglob("*.py"))


def test_no_direct_mdb_write_path():
    text = source_text().casefold()
    forbidden = (
        "update slibv1001",
        "insert into slibv1001",
        "delete from slibv1001",
        "adodb.connection",
        "pyodbc.connect",
    )
    assert all(token not in text for token in forbidden)


def test_no_automatic_save_call():
    text = source_text().casefold()
    forbidden = (
        'click_input(title="simpan',
        'child_window(title="simpan',
        ".save_record(",
    )
    assert all(token not in text for token in forbidden)
