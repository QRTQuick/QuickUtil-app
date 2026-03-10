from __future__ import annotations

import time
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QSystemTrayIcon


@dataclass(frozen=True)
class Notification:
    ts: int
    level: str  # info | warning | alarm | reminder
    title: str
    message: str


class NotificationService(QObject):
    notification_added = Signal(object)  # Notification
    cleared = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._items: list[Notification] = []
        self._tray: QSystemTrayIcon | None = None

    def set_tray_icon(self, tray: QSystemTrayIcon | None) -> None:
        self._tray = tray

    def items(self) -> list[Notification]:
        return list(self._items)

    def clear(self) -> None:
        self._items.clear()
        self.cleared.emit()

    def add(self, *, level: str, title: str, message: str, toast: bool = True) -> Notification:
        n = Notification(ts=int(time.time()), level=level, title=title, message=message)
        self._items.insert(0, n)
        if len(self._items) > 250:
            self._items = self._items[:250]

        self.notification_added.emit(n)

        if toast and self._tray and self._tray.isVisible():
            icon = QSystemTrayIcon.MessageIcon.Information
            if level in {"warning"}:
                icon = QSystemTrayIcon.MessageIcon.Warning
            elif level in {"alarm", "reminder"}:
                icon = QSystemTrayIcon.MessageIcon.Critical
            try:
                self._tray.showMessage(title, message, icon, 6000)
            except Exception:
                pass

        return n

    def info(self, title: str, message: str, *, toast: bool = False) -> Notification:
        return self.add(level="info", title=title, message=message, toast=toast)

    def warning(self, title: str, message: str, *, toast: bool = True) -> Notification:
        return self.add(level="warning", title=title, message=message, toast=toast)

    def alarm(self, title: str, message: str, *, toast: bool = True) -> Notification:
        return self.add(level="alarm", title=title, message=message, toast=toast)

    def reminder(self, title: str, message: str, *, toast: bool = True) -> Notification:
        return self.add(level="reminder", title=title, message=message, toast=toast)

