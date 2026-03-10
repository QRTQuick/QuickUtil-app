import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:table_calendar/table_calendar.dart';

import '../database/database_helper.dart';
import '../models/event_model.dart';

DateTime _dayKey(DateTime d) => DateTime(d.year, d.month, d.day);

class CalendarScreen extends StatefulWidget {
  const CalendarScreen({super.key});

  @override
  State<CalendarScreen> createState() => _CalendarScreenState();
}

class _CalendarScreenState extends State<CalendarScreen> {
  final _db = DatabaseHelper.instance;
  final _fmt = DateFormat('EEE, MMM d');

  DateTime _focused = DateTime.now();
  DateTime _selected = _dayKey(DateTime.now());
  Map<DateTime, List<EventModel>> _eventsByDay = {};

  @override
  void initState() {
    super.initState();
    _loadMonth(_focused);
  }

  Future<void> _loadMonth(DateTime focused) async {
    final start = DateTime(focused.year, focused.month, 1);
    final end = DateTime(focused.year, focused.month + 1, 1);
    final events = await _db.eventsInRange(start, end);

    final map = <DateTime, List<EventModel>>{};
    for (final e in events) {
      final k = _dayKey(e.start);
      map.putIfAbsent(k, () => []).add(e);
    }
    if (!mounted) return;
    setState(() => _eventsByDay = map);
  }

  List<EventModel> _eventsForDay(DateTime day) => _eventsByDay[_dayKey(day)] ?? const [];

  Future<void> _addEvent() async {
    final title = await _promptText('New event', 'Title');
    if (title == null || title.trim().isEmpty) return;

    final time = await showTimePicker(context: context, initialTime: const TimeOfDay(hour: 9, minute: 0));
    final when = DateTime(_selected.year, _selected.month, _selected.day, time?.hour ?? 9, time?.minute ?? 0);

    await _db.insertEvent(EventModel(title: title.trim(), start: when));
    await _loadMonth(_focused);
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Event added')));
  }

  Future<void> _editEvent(EventModel e) async {
    final title = await _promptText('Edit event', 'Title', initial: e.title);
    if (title == null || title.trim().isEmpty) return;

    await _db.updateEvent(EventModel(id: e.id, title: title.trim(), start: e.start, end: e.end, notes: e.notes));
    await _loadMonth(_focused);
  }

  Future<void> _deleteEvent(EventModel e) async {
    if (e.id == null) return;
    await _db.deleteEvent(e.id!);
    await _loadMonth(_focused);
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
    final selectedEvents = _eventsForDay(_selected);

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Row(
          children: [
            Expanded(
              child: Text('Calendar', style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.w800)),
            ),
            FilledButton.icon(onPressed: _addEvent, icon: const Icon(Icons.add), label: const Text('Add')),
          ],
        ),
        const SizedBox(height: 12),
        Card(
          elevation: 0,
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: TableCalendar<EventModel>(
              firstDay: DateTime.utc(2000, 1, 1),
              lastDay: DateTime.utc(2100, 12, 31),
              focusedDay: _focused,
              selectedDayPredicate: (day) => isSameDay(day, _selected),
              calendarFormat: CalendarFormat.month,
              eventLoader: _eventsForDay,
              onDaySelected: (selected, focused) => setState(() {
                _selected = _dayKey(selected);
                _focused = focused;
              }),
              onPageChanged: (focused) {
                _focused = focused;
                _loadMonth(focused);
              },
            ),
          ),
        ),
        const SizedBox(height: 12),
        Text('Events • ${_fmt.format(_selected)}', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        if (selectedEvents.isEmpty)
          const Text('No events for this day.', style: TextStyle(color: Colors.white70))
        else
          ...selectedEvents.map(
            (e) => Card(
              elevation: 0,
              child: ListTile(
                title: Text(e.title),
                subtitle: Text(DateFormat('HH:mm').format(e.start)),
                trailing: PopupMenuButton<String>(
                  onSelected: (v) => v == 'edit' ? _editEvent(e) : _deleteEvent(e),
                  itemBuilder: (_) => const [
                    PopupMenuItem(value: 'edit', child: Text('Edit')),
                    PopupMenuItem(value: 'delete', child: Text('Delete')),
                  ],
                ),
              ),
            ),
          ),
      ],
    );
  }
}

