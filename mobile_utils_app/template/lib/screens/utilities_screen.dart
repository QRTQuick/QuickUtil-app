import 'package:flutter/material.dart';

import 'alarm_screen.dart';
import 'notification_center_screen.dart';
import 'wallpaper_editor_screen.dart';

class UtilitiesScreen extends StatelessWidget {
  const UtilitiesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text('Utilities', style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.w800)),
        const SizedBox(height: 6),
        Text('Productivity and customization modules.', style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.white70)),
        const SizedBox(height: 14),
        Card(
          elevation: 0,
          child: Column(
            children: [
              ListTile(
                leading: const Icon(Icons.alarm),
                title: const Text('Alarms & Reminders'),
                subtitle: const Text('Schedule local notifications'),
                onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const AlarmScreen())),
              ),
              const Divider(height: 1),
              ListTile(
                leading: const Icon(Icons.notifications),
                title: const Text('Notification Center'),
                subtitle: const Text('In-app notification log'),
                onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const NotificationCenterScreen())),
              ),
              const Divider(height: 1),
              ListTile(
                leading: const Icon(Icons.wallpaper),
                title: const Text('Wallpaper Editor'),
                subtitle: const Text('Import, filter, save'),
                onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const WallpaperEditorScreen())),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

