from __future__ import annotations

import argparse
import ctypes
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path


APP_EXE_NAME = "SLibAssistant.exe"
WAIT_TIMEOUT_MS = 120_000


def _data_dir() -> Path:
    root = os.environ.get("LOCALAPPDATA")
    if root:
        return Path(root) / "SLibAssistant"
    return Path.home() / ".slib-assistant"


def _log(message: str) -> None:
    path = _data_dir() / "update.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{stamp} {message}\n")


def _message(title: str, message: str, error: bool = False) -> None:
    if os.name != "nt":
        return
    flags = 0x10 if error else 0x40
    try:
        ctypes.windll.user32.MessageBoxW(None, message, title, flags)
    except Exception:
        pass


def wait_for_process(pid: int, timeout_ms: int = WAIT_TIMEOUT_MS) -> None:
    if pid <= 0 or os.name != "nt":
        return
    SYNCHRONIZE = 0x00100000
    handle = ctypes.windll.kernel32.OpenProcess(SYNCHRONIZE, False, pid)
    if not handle:
        return
    try:
        result = ctypes.windll.kernel32.WaitForSingleObject(handle, timeout_ms)
        if result == 0x00000102:
            raise RuntimeError("S-Lib Assistant tidak tutup dalam tempoh yang dibenarkan.")
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)


def install_package(package: Path, target: Path) -> None:
    package = package.resolve()
    target = target.resolve()
    if target.name.lower() != APP_EXE_NAME.lower():
        raise RuntimeError("Target kemas kini bukan SLibAssistant.exe.")
    if not package.is_file():
        raise RuntimeError("Pakej kemas kini tidak ditemui.")
    if not target.parent.is_dir():
        raise RuntimeError("Folder pemasangan tidak sah.")

    backup = target.with_suffix(target.suffix + ".bak")
    with tempfile.TemporaryDirectory(prefix="slib-update-") as temp_dir:
        temp_root = Path(temp_dir)
        with zipfile.ZipFile(package, "r") as archive:
            member = next(
                (
                    item
                    for item in archive.infolist()
                    if Path(item.filename).name.lower() == APP_EXE_NAME.lower()
                    and not item.is_dir()
                ),
                None,
            )
            if member is None:
                raise RuntimeError("Pakej tidak mengandungi SLibAssistant.exe.")
            extracted = temp_root / APP_EXE_NAME
            with archive.open(member, "r") as source, extracted.open("wb") as dest:
                shutil.copyfileobj(source, dest)

        if backup.exists():
            backup.unlink()
        if target.exists():
            shutil.copy2(target, backup)
        try:
            shutil.copy2(extracted, target)
        except Exception:
            if backup.exists():
                shutil.copy2(backup, target)
            raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="S-Lib Assistant safe updater")
    parser.add_argument("--package", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--pid", type=int, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    package = Path(args.package)
    target = Path(args.target)
    try:
        _log(f"Update requested for {target}")
        wait_for_process(args.pid)
        install_package(package, target)
        _log("Update installed successfully.")
        subprocess.Popen([str(target)], cwd=str(target.parent), close_fds=True)
        return 0
    except Exception as exc:
        _log(f"Update failed: {exc}")
        _message(
            "S-Lib Assistant — Kemas Kini Gagal",
            f"Kemas kini tidak dapat dipasang. Versi sebelumnya dikekalkan.\n\n{exc}",
            error=True,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
