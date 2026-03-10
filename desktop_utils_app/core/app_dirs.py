from __future__ import annotations

import os
import platform
from pathlib import Path


def data_dir(app_name: str = "QuickUtil") -> Path:
    """
    Cross-platform user data directory.

    - Windows: %LOCALAPPDATA%/QuickUtil
    - macOS: ~/Library/Application Support/QuickUtil
    - Linux: $XDG_DATA_HOME/quickutil or ~/.local/share/quickutil
    """

    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if base:
            return Path(base) / app_name
        return Path.home() / "AppData" / "Local" / app_name

    if platform.system().lower() == "darwin":
        return Path.home() / "Library" / "Application Support" / app_name

    base = os.environ.get("XDG_DATA_HOME")
    if base:
        return Path(base) / app_name.lower()
    return Path.home() / ".local" / "share" / app_name.lower()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def db_path(app_name: str = "QuickUtil") -> Path:
    return ensure_dir(data_dir(app_name)) / "quickutil.db"

