import 'package:flutter/material.dart';

class NotificationCenterScreen extends StatelessWidget {
  const NotificationCenterScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Notification Center')),
      body: const Padding(
        padding: EdgeInsets.all(16),
        child: Text(
          'In-app notification history can be extended to log alarms, reminders, and system alerts.\n\n'
          'This scaffold focuses on a clean UI and CI-ready build.',
          style: TextStyle(color: Colors.white70),
        ),
      ),
    );
  }
}

