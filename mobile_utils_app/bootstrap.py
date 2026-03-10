from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path
import re


def _run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.check_call(cmd, cwd=str(cwd) if cwd else None)

def _patch_android_build(out: Path) -> None:
    """
    flutter_local_notifications (v10+) requires desugaring + Java 17 for scheduling support.
    Keep changes minimal and idempotent.
    """

    build_gradle = out / "android" / "app" / "build.gradle"
    if not build_gradle.exists():
        return

    text = build_gradle.read_text(encoding="utf-8")
    original = text

    text = text.replace("JavaVersion.VERSION_1_8", "JavaVersion.VERSION_17")

    if "coreLibraryDesugaringEnabled true" not in text and "compileOptions {" in text:
        text = text.replace("compileOptions {", "compileOptions {\n        coreLibraryDesugaringEnabled true", 1)

    if "multiDexEnabled true" not in text and "defaultConfig {" in text:
        text = text.replace("defaultConfig {", "defaultConfig {\n        multiDexEnabled true", 1)

    if "coreLibraryDesugaring 'com.android.tools:desugar_jdk_libs:" not in text and "dependencies {" in text:
        text = text.replace(
            "dependencies {",
            "dependencies {\n    coreLibraryDesugaring 'com.android.tools:desugar_jdk_libs:2.1.4'",
            1,
        )

    # Ensure kotlinOptions jvmTarget is 17 if present.
    text = re.sub(r"jvmTarget\s*=\s*['\"]1\\.8['\"]", "jvmTarget = '17'", text)
    text = re.sub(r"jvmTarget\s*=\s*JavaVersion\\.VERSION_1_8\\.toString\\(\\)", "jvmTarget = '17'", text)

    if text != original:
        build_gradle.write_text(text, encoding="utf-8")

def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a buildable Flutter project from the template.")
    parser.add_argument("--out", default="mobile_utils_app/app", help="Output directory (generated Flutter project).")
    parser.add_argument("--org", default="com.quickutil", help="Android/iOS organization identifier.")
    parser.add_argument("--name", default="mobile_utils_app", help="Flutter project name.")
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    template = here / "template"
    out = Path(args.out).resolve()

    out.parent.mkdir(parents=True, exist_ok=True)

    if not out.exists():
        _run(
            [
                "flutter",
                "create",
                "--platforms=android,ios",
                "--org",
                args.org,
                "--project-name",
                args.name,
                str(out),
            ]
        )

    _patch_android_build(out)

    # Replace template-controlled files.
    for p in ["lib", "assets"]:
        dst = out / p
        if dst.exists():
            shutil.rmtree(dst, ignore_errors=True)
        src = template / p
        if src.exists():
            shutil.copytree(src, dst)

    shutil.copy2(template / "pubspec.yaml", out / "pubspec.yaml")

    _run(["flutter", "pub", "get"], cwd=out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
