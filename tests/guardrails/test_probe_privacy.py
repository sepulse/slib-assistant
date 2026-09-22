from types import SimpleNamespace

from slib_assistant.slib.probe import _safe_control


def test_edit_control_name_is_redacted():
    info = SimpleNamespace(
        control_type="Edit",
        class_name="Edit",
        automation_id="123",
        name="PRIVATE CONTENT",
        rectangle=None,
        enabled=True,
        visible=True,
    )
    control = SimpleNamespace(element_info=info)
    output = _safe_control(control)
    assert output["name"] == "<editable-content-redacted>"
    assert "PRIVATE" not in str(output)
