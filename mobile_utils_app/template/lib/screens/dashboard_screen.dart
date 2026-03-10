import 'package:flutter/material.dart';

import '../widgets/stat_card.dart';
import 'alarm_screen.dart';
import 'calendar_screen.dart';
import 'system_monitor_screen.dart';
import 'wallpaper_editor_screen.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text('Dashboard', style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.w800)),
        const SizedBox(height: 6),
        Text('Quick actions and highlights.', style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.white70)),
        const SizedBox(height: 14),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
          childAspectRatio: 1.25,
          children: [
            StatCard(
              title: 'System Monitor',
              child: const Text('CPU • RAM • Battery', style: TextStyle(color: Colors.white70)),
              onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const SystemMonitorScreen())),
            ),
            StatCard(
              title: 'Calendar',
              child: const Text('Events • Reminders', style: TextStyle(color: Colors.white70)),
              onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const CalendarScreen())),
            ),
            StatCard(
              title: 'Alarms',
              child: const Text('Local notifications', style: TextStyle(color: Colors.white70)),
              onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const AlarmScreen())),
            ),
            StatCard(
              title: 'Wallpaper',
              child: const Text('Import • Filter • Save', style: TextStyle(color: Colors.white70)),
              onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const WallpaperEditorScreen())),
            ),
          ],
        ),
      ],
    );
  }
}

