from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def _sep() -> str:
    return ";" if os.name == "nt" else ":"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)

    dist = root / "dist"
    build = root / "build"
    for p in (dist, build):
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)

    add_data = f"{root / 'desktop_utils_app' / 'assets'}{_sep()}assets"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        "QuickUtil",
        "--add-data",
        add_data,
        "--hidden-import",
        "PySide6.QtSvg",
        "--hidden-import",
        "PIL.ImageQt",
        str(root / "desktop_utils_app" / "main.py"),
    ]

    print("Building QuickUtil with PyInstaller…")
    print("OS:", platform.platform())
    print("CMD:", " ".join(cmd))
    subprocess.check_call(cmd)
    print("Build complete:", dist)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

