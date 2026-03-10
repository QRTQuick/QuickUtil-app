# QuickUtil-app
QuickUtil is a cross-platform **desktop + mobile** utility suite:

- **Desktop (Python + PySide6)**: system monitor, calendar, alarms/reminders, notification center, wallpaper editor.
- **Mobile (Flutter/Dart)**: modern dark UI with bottom navigation, plus scaffolded utility modules.

## Desktop (PySide6)
- Install: `pip install -r desktop_utils_app/requirements.txt`
- Run: `python desktop_utils_app/main.py`
- Build (PyInstaller): `pip install -r desktop_utils_app/requirements-dev.txt` then `python desktop_utils_app/build.py`

## Mobile (Flutter)
This repo keeps a Flutter **template** and bootstraps a full buildable project (Android/iOS) via `flutter create`.

- Generate project: `python mobile_utils_app/bootstrap.py --out mobile_utils_app/app`
- Run: `cd mobile_utils_app/app` then `flutter run`

## CI/CD
GitHub Actions builds artifacts on cloud runners (no local builds required):

- Desktop: `.github/workflows/desktop-build.yml` (Windows `.exe` + macOS `.app`)
- Mobile: `.github/workflows/mobile-build.yml` (Android APK+AAB + iOS **simulator** `.app` zip)
