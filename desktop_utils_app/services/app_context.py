from __future__ import annotations

from PySide6.QtCore import QObject

from database.db import Database
from services.alarm_scheduler import AlarmScheduler
from services.notification_service import NotificationService
from services.system_watcher import SystemWatcher


class AppContext(QObject):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.db = Database()
        self.notifications = NotificationService(self)
        self.alarm_scheduler = AlarmScheduler(self.db, self.notifications, self)
        self.system_watcher = SystemWatcher(self.notifications, parent=self)

