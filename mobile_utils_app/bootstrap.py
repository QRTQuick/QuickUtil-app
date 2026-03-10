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

    def insert_after_first_line(text: str, pattern: str, insert_line: str) -> str:
        m = re.search(pattern, text, flags=re.MULTILINE)
        if not m:
            return text
        idx = m.end()
        return text[:idx] + "\n" + insert_line + text[idx:]

    def ensure_dependency(text: str, *, kts: bool) -> str:
        if kts:
            dep_line = 'coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")'
            if "coreLibraryDesugaring(\"com.android.tools:desugar_jdk_libs:" in text:
                return text
        else:
            dep_line = "coreLibraryDesugaring 'com.android.tools:desugar_jdk_libs:2.1.4'"
            if "coreLibraryDesugaring 'com.android.tools:desugar_jdk_libs:" in text or 'coreLibraryDesugaring "com.android.tools:desugar_jdk_libs:' in text:
                return text

        # Insert into existing dependencies block if present, else append one.
        deps_pat = r"^\s*dependencies\s*\{\s*$"
        if re.search(deps_pat, text, flags=re.MULTILINE):
            return insert_after_first_line(text, deps_pat, f"    {dep_line}")

        suffix = "\n" if text.endswith("\n") else "\n\n"
        return text + suffix + "dependencies {\n" + f"    {dep_line}\n" + "}\n"

    for build_gradle in [
        out / "android" / "app" / "build.gradle",
        out / "android" / "app" / "build.gradle.kts",
    ]:
        if not build_gradle.exists():
            continue

        text = build_gradle.read_text(encoding="utf-8")
        original = text

        text = text.replace("JavaVersion.VERSION_1_8", "JavaVersion.VERSION_17")

        if build_gradle.name.endswith(".kts"):
            if "isCoreLibraryDesugaringEnabled" not in text:
                text = insert_after_first_line(
                    text,
                    r"^\s*compileOptions\s*\{\s*$",
                    "        isCoreLibraryDesugaringEnabled = true",
                )

            if "multiDexEnabled" not in text and "defaultConfig {" in text:
                text = text.replace("defaultConfig {", "defaultConfig {\n        multiDexEnabled = true", 1)

            text = ensure_dependency(text, kts=True)

            text = re.sub(r"jvmTarget\s*=\s*['\"]1\\.8['\"]", 'jvmTarget = "17"', text)
            text = re.sub(r"jvmTarget\s*=\s*JavaVersion\\.VERSION_1_8\\.toString\\(\\)", 'jvmTarget = "17"', text)
        else:
            if "coreLibraryDesugaringEnabled" not in text:
                text = insert_after_first_line(
                    text,
                    r"^\s*compileOptions\s*\{\s*$",
                    "        coreLibraryDesugaringEnabled true",
                )

            if "multiDexEnabled true" not in text and "defaultConfig {" in text:
                text = text.replace("defaultConfig {", "defaultConfig {\n        multiDexEnabled true", 1)

            text = ensure_dependency(text, kts=False)

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
