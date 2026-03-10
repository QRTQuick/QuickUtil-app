import 'package:flutter/material.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text('Settings', style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.w800)),
        const SizedBox(height: 6),
        const Text('Theme and preferences (extensible).', style: TextStyle(color: Colors.white70)),
        const SizedBox(height: 14),
        Card(
          elevation: 0,
          child: ListTile(
            leading: const Icon(Icons.info_outline),
            title: const Text('About QuickUtil'),
            subtitle: const Text('Mobile utility suite'),
            onTap: () => showAboutDialog(
              context: context,
              applicationName: 'QuickUtil',
              applicationVersion: '0.1.0',
            ),
          ),
        ),
      ],
    );
  }
}

