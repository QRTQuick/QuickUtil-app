class AlarmModel {
  final int? id;
  final String label;
  final DateTime when;
  final bool enabled;
  final String kind; // alarm | reminder

  AlarmModel({
    this.id,
    required this.label,
    required this.when,
    required this.enabled,
    required this.kind,
  });

  Map<String, Object?> toMap() => {
        'id': id,
        'label': label,
        'ts': when.millisecondsSinceEpoch,
        'enabled': enabled ? 1 : 0,
        'kind': kind,
      };

  static AlarmModel fromMap(Map<String, Object?> map) => AlarmModel(
        id: map['id'] as int?,
        label: map['label'] as String,
        when: DateTime.fromMillisecondsSinceEpoch(map['ts'] as int),
        enabled: (map['enabled'] as int) == 1,
        kind: map['kind'] as String,
      );
}

