import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:sqflite/sqflite.dart';

import '../models/alarm_model.dart';
import '../models/event_model.dart';

class DatabaseHelper {
  DatabaseHelper._();

  static final DatabaseHelper instance = DatabaseHelper._();
  Database? _db;

  Future<Database> get database async => _db ??= await _init();

  Future<Database> _init() async {
    final dir = await getApplicationDocumentsDirectory();
    final path = p.join(dir.path, 'quickutil_mobile.db');
    return openDatabase(
      path,
      version: 1,
      onCreate: (db, _) async {
        await db.execute('''
          CREATE TABLE events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            start_ts INTEGER NOT NULL,
            end_ts INTEGER,
            notes TEXT
          );
        ''');
        await db.execute('CREATE INDEX idx_events_start ON events(start_ts);');

        await db.execute('''
          CREATE TABLE alarms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT NOT NULL,
            ts INTEGER NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1,
            kind TEXT NOT NULL DEFAULT 'alarm'
          );
        ''');
        await db.execute('CREATE INDEX idx_alarms_ts ON alarms(ts);');
      },
    );
  }

  Future<List<EventModel>> eventsForDay(DateTime day) async {
    final db = await database;
    final start = DateTime(day.year, day.month, day.day);
    final end = start.add(const Duration(days: 1));
    final rows = await db.query(
      'events',
      where: 'start_ts >= ? AND start_ts < ?',
      whereArgs: [start.millisecondsSinceEpoch, end.millisecondsSinceEpoch],
      orderBy: 'start_ts ASC',
    );
    return rows.map((e) => EventModel.fromMap(e)).toList();
  }

  Future<List<EventModel>> eventsInRange(DateTime start, DateTime end) async {
    final db = await database;
    final rows = await db.query(
      'events',
      where: 'start_ts >= ? AND start_ts < ?',
      whereArgs: [start.millisecondsSinceEpoch, end.millisecondsSinceEpoch],
      orderBy: 'start_ts ASC',
    );
    return rows.map((e) => EventModel.fromMap(e)).toList();
  }

  Future<int> insertEvent(EventModel event) async {
    final db = await database;
    return db.insert('events', event.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<int> updateEvent(EventModel event) async {
    final db = await database;
    return db.update('events', event.toMap(), where: 'id = ?', whereArgs: [event.id]);
  }

  Future<int> deleteEvent(int id) async {
    final db = await database;
    return db.delete('events', where: 'id = ?', whereArgs: [id]);
  }

  Future<List<AlarmModel>> listAlarms() async {
    final db = await database;
    final rows = await db.query('alarms', orderBy: 'ts ASC');
    return rows.map((e) => AlarmModel.fromMap(e)).toList();
  }

  Future<int> insertAlarm(AlarmModel alarm) async {
    final db = await database;
    return db.insert('alarms', alarm.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<int> updateAlarm(AlarmModel alarm) async {
    final db = await database;
    return db.update('alarms', alarm.toMap(), where: 'id = ?', whereArgs: [alarm.id]);
  }

  Future<int> deleteAlarm(int id) async {
    final db = await database;
    return db.delete('alarms', where: 'id = ?', whereArgs: [id]);
  }
}

