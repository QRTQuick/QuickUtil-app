from __future__ import annotations

import os
import platform
import subprocess
import tempfile
from pathlib import Path


def _run(cmd: list[str], *, timeout: int = 8) -> tuple[bool, str]:
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return True, "OK"
    except Exception as e:
        return False, str(e)


def apply_wallpaper(path: Path) -> tuple[bool, str]:
    """
    Best-effort wallpaper apply across platforms.
    Returns (success, message).
    """

    path = Path(path).expanduser().resolve()
    if not path.exists():
        return False, "File does not exist."

    sysname = platform.system().lower()

    if sysname == "windows":
        try:
            import ctypes

            SPI_SETDESKWALLPAPER = 20
            SPIF_UPDATEINIFILE = 0x01
            SPIF_SENDCHANGE = 0x02

            # Windows is most reliable with BMP.
            try:
                from PIL import Image  # type: ignore

                bmp_path = Path(tempfile.gettempdir()) / "quickutil_wallpaper.bmp"
                Image.open(path).convert("RGB").save(bmp_path, "BMP")
                target = str(bmp_path)
            except Exception:
                target = str(path)

            ok = ctypes.windll.user32.SystemParametersInfoW(  # type: ignore[attr-defined]
                SPI_SETDESKWALLPAPER, 0, target, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
            )
            return (bool(ok), "Wallpaper applied." if ok else "Failed to apply wallpaper.")
        except Exception as e:
            return False, f"Windows apply failed: {e}"

    if sysname == "darwin":
        script = (
            'tell application "System Events"\n'
            f'  set picture of every desktop to POSIX file "{path.as_posix()}"\n'
            "end tell"
        )
        ok, msg = _run(["osascript", "-e", script], timeout=10)
        return ok, "Wallpaper applied." if ok else f"macOS apply failed: {msg}"

    # Linux (GNOME) via gsettings
    if os.environ.get("XDG_CURRENT_DESKTOP", "").lower().find("gnome") >= 0:
        uri = f"file://{path.as_posix()}"
        ok1, msg1 = _run(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri])
        ok2, _ = _run(["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", uri])
        if ok1 or ok2:
            return True, "Wallpaper applied (GNOME)."
        return False, f"GNOME apply failed: {msg1}"

    # Linux fallback: feh (common in lightweight WMs)
    ok, msg = _run(["feh", "--bg-fill", str(path)])
    if ok:
        return True, "Wallpaper applied (feh)."

    return False, "Unsupported desktop environment (tried GNOME/feh)."

