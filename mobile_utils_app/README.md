# QuickUtil Mobile (Flutter)

This repo stores a Flutter **template** under `mobile_utils_app/template/` and generates a full buildable Flutter project (Android/iOS) via `flutter create`.

## Generate a runnable project

```bash
python mobile_utils_app/bootstrap.py --out mobile_utils_app/app
cd mobile_utils_app/app
flutter run
```

## CI

GitHub Actions uses the same bootstrap step and produces:

- Android: APK + AAB
- iOS: `.app` zip (no codesign)

