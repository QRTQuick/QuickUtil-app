class EventModel {
  final int? id;
  final String title;
  final DateTime start;
  final DateTime? end;
  final String? notes;

  EventModel({
    this.id,
    required this.title,
    required this.start,
    this.end,
    this.notes,
  });

  Map<String, Object?> toMap() => {
        'id': id,
        'title': title,
        'start_ts': start.millisecondsSinceEpoch,
        'end_ts': end?.millisecondsSinceEpoch,
        'notes': notes,
      };

  static EventModel fromMap(Map<String, Object?> map) => EventModel(
        id: map['id'] as int?,
        title: map['title'] as String,
        start: DateTime.fromMillisecondsSinceEpoch(map['start_ts'] as int),
        end: map['end_ts'] == null ? null : DateTime.fromMillisecondsSinceEpoch(map['end_ts'] as int),
        notes: map['notes'] as String?,
      );
}

