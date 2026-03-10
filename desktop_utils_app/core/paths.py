from __future__ import annotations

import sys
from pathlib import Path


def app_root() -> Path:
    # `main.py` lives at the app root directory.
    return Path(__file__).resolve().parents[1]


def resource_path(*parts: str) -> str:
    """
    Return an absolute path to an asset, working in dev and in PyInstaller builds.
    """

    base = getattr(sys, "_MEIPASS", None)
    if base:
        return str(Path(base, *parts))
    return str(app_root().joinpath(*parts))

