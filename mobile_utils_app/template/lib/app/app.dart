import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import 'app_shell.dart';

class QuickUtilApp extends StatelessWidget {
  const QuickUtilApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'QuickUtil',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.dark(),
      home: const AppShell(),
    );
  }
}

