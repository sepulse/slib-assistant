from __future__ import annotations

import argparse
import json
import platform
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SENSITIVE_TYPES = {"Edit", "Document", "ComboBox"}


def _safe_control(control: Any) -> dict[str, Any]:
    info = control.element_info
    control_type = str(getattr(info, "control_type", "") or "")
    name = str(getattr(info, "name", "") or "")
    if control_type in SENSITIVE_TYPES:
        name = "<editable-content-redacted>"
    rectangle = getattr(info, "rectangle", None)
    rect = None if rectangle is None else [rectangle.left, rectangle.top, rectangle.right, rectangle.bottom]
    return {
        "control_type": control_type,
        "class_name": str(getattr(info, "class_name", "") or ""),
        "automation_id": str(getattr(info, "automation_id", "") or ""),
        "name": name,
        "rectangle": rect,
        "enabled": bool(getattr(info, "enabled", False)),
        "visible": bool(getattr(info, "visible", False)),
    }


def run_probe(window_title: str) -> dict[str, Any]:
    result = {
        "slib_detected": False,
        "window_title": "",
        "process_name": "",
        "process_id": None,
        "controls": [],
        "tab_order_observations": [],
        "notes": [],
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        from pywinauto import Desktop
    except ImportError:
        result["notes"].append("pywinauto is not installed.")
        return result
    try:
        window = Desktop(backend="uia").window(title_re=".*" + re.escape(window_title) + ".*")
        if not window.exists(timeout=2):
            result["notes"].append("Target window not found.")
            return result
        result["slib_detected"] = True
        result["window_title"] = window.window_text()
        try:
            result["process_id"] = window.process_id()
            try:
                from pywinauto.application import process_module
                result["process_name"] = Path(
                    process_module(result["process_id"])
                ).name
            except Exception:
                result["process_name"] = ""
        except Exception:
            result["process_id"] = None
        result["controls"] = [_safe_control(x) for x in window.descendants()]
    except Exception as exc:
        result["notes"].append(f"Probe error: {type(exc).__name__}: {exc}")
    return result


def write_probe_output(result: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "probe.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = []
    for index, control in enumerate(result.get("controls", [])):
        lines.append(f"{index:04d} {control.get('control_type', ''):12} class={control.get('class_name', '')} automation_id={control.get('automation_id', '')} name={control.get('name', '')} rect={control.get('rectangle')}")
    (output_dir / "controls.txt").write_text("\n".join(lines), encoding="utf-8")
    environment = {"os": platform.platform(), "python": sys.version, "machine": platform.machine()}
    (output_dir / "environment.txt").write_text(json.dumps(environment, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only S-Lib control probe.")
    parser.add_argument("--title", default="Kemaskini Bahan")
    parser.add_argument("--output", default="probe-output")
    args = parser.parse_args(argv)
    output_dir = Path(args.output)
    result = run_probe(args.title)
    write_probe_output(result, output_dir)
    print(f"Probe output: {output_dir.resolve()}")
    print(f"S-Lib detected: {result['slib_detected']}")
    return 0 if result["slib_detected"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
