import pytest

from slib_assistant.config import load_config


def test_auto_save_true_is_rejected(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('[slib]\nauto_save = true\n', encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(path)


def test_missing_config_is_created_with_auto_save_off(tmp_path):
    path = tmp_path / "config.toml"
    config = load_config(path)
    assert path.exists()
    assert "auto_save = false" in path.read_text(encoding="utf-8")
    assert config.auto_save is False
