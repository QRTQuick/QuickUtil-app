import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../database/database_helper.dart';
import '../models/alarm_model.dart';
import '../services/notification_service.dart';

class AlarmScreen extends StatefulWidget {
  const AlarmScreen({super.key});

  @override
  State<AlarmScreen> createState() => _AlarmScreenState();
}

class _AlarmScreenState extends State<AlarmScreen> {
  final _db = DatabaseHelper.instance;
  final _fmt = DateFormat('y-MM-dd HH:mm');

  List<AlarmModel> _alarms = const [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final rows = await _db.listAlarms();
    if (!mounted) return;
    setState(() => _alarms = rows);
  }

  Future<void> _add() async {
    final label = await _promptText('New alarm', 'Label');
    if (label == null || label.trim().isEmpty) return;

    final date = await showDatePicker(
      context: context,
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 3650)),
      initialDate: DateTime.now().add(const Duration(minutes: 10)),
    );
    if (date == null) return;

    final time = await showTimePicker(context: context, initialTime: const TimeOfDay(hour: 9, minute: 0));
    final when = DateTime(date.year, date.month, date.day, time?.hour ?? 9, time?.minute ?? 0);

    final id = await _db.insertAlarm(AlarmModel(label: label.trim(), when: when, enabled: true, kind: 'alarm'));
    await NotificationService.instance.schedule(id: id, title: 'Alarm', body: label.trim(), when: when);
    await _load();
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Alarm scheduled')));
  }

  Future<void> _toggle(AlarmModel a, bool enabled) async {
    if (a.id == null) return;
    final updated = AlarmModel(id: a.id, label: a.label, when: a.when, enabled: enabled, kind: a.kind);
    await _db.updateAlarm(updated);
    if (enabled) {
      await NotificationService.instance.schedule(id: a.id!, title: 'Alarm', body: a.label, when: a.when);
    } else {
      await NotificationService.instance.cancel(a.id!);
    }
    await _load();
  }

  Future<void> _delete(AlarmModel a) async {
    if (a.id == null) return;
    await _db.deleteAlarm(a.id!);
    await NotificationService.instance.cancel(a.id!);
    await _load();
  }

  Future<String?> _promptText(String title, String label, {String initial = ''}) async {
    final controller = TextEditingController(text: initial);
    return showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(title),
        content: TextField(
          controller: controller,
          decoration: InputDecoration(labelText: label),
          autofocus: true,
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(ctx, controller.text), child: const Text('Save')),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Alarms & Reminders')),
      floatingActionButton: FloatingActionButton(onPressed: _add, child: const Icon(Icons.add)),
      body: ListView(
        padding: const EdgeInsets.all(12),
        children: [
          if (_alarms.isEmpty)
            const Padding(
              padding: EdgeInsets.all(12),
              child: Text('No alarms scheduled.', style: TextStyle(color: Colors.white70)),
            ),
          ..._alarms.map(
            (a) => Card(
              elevation: 0,
              child: ListTile(
                title: Text(a.label),
                subtitle: Text(_fmt.format(a.when)),
                leading: Switch(value: a.enabled, onChanged: (v) => _toggle(a, v)),
                trailing: IconButton(icon: const Icon(Icons.delete_outline), onPressed: () => _delete(a)),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

