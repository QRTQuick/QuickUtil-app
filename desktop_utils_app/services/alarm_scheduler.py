from __future__ import annotations

import time
from datetime import datetime

from PySide6.QtCore import QObject, QTimer

from database.alarms import due_alarms, mark_alarm_fired
from database.db import Database
from services.notification_service import NotificationService


class AlarmScheduler(QObject):
    def __init__(self, db: Database, notifications: NotificationService, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._db = db
        self._notifications = notifications

        self._timer = QTimer(self)
        self._timer.setInterval(800)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _tick(self) -> None:
        now_ts = int(time.time())
        for alarm in due_alarms(self._db, now_ts=now_ts):
            when = datetime.fromtimestamp(alarm.ts).strftime("%Y-%m-%d %H:%M")
            title = "Alarm" if alarm.kind == "alarm" else "Reminder"
            self._notifications.add(level=alarm.kind, title=f"{title} • {when}", message=alarm.label, toast=True)
            mark_alarm_fired(self._db, alarm_id=alarm.id, fired=True)

