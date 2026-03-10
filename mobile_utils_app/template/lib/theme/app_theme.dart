import 'package:flutter/material.dart';

class AppTheme {
  static const _bg = Color(0xFF0B0B0D);
  static const _surface = Color(0xFF14141A);
  static const _surface2 = Color(0xFF1C1C24);
  static const _border = Color(0xFF2A2A35);
  static const _accent = Color(0xFFE11D48); // red
  static const _info = Color(0xFF38BDF8); // sky (secondary)

  static ThemeData dark() {
    final scheme = ColorScheme.fromSeed(
      seedColor: _accent,
      brightness: Brightness.dark,
      surface: _surface,
    ).copyWith(
      primary: _accent,
      secondary: _info,
      surface: _surface,
      surfaceContainerHighest: _surface2,
      outline: _border,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: _bg,
      cardColor: _surface,
      snackBarTheme: const SnackBarThemeData(behavior: SnackBarBehavior.floating),
    );
  }
}

