from __future__ import annotations

import time

from PySide6.QtCore import QObject, QTimer

from services.notification_service import NotificationService
from system.collector import collect_snapshot


class SystemWatcher(QObject):
    def __init__(
        self,
        notifications: NotificationService,
        *,
        cpu_warn: float = 92.0,
        mem_warn: float = 92.0,
        cooldown_seconds: int = 60,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._notifications = notifications
        self._cpu_warn = cpu_warn
        self._mem_warn = mem_warn
        self._cooldown = cooldown_seconds
        self._last_cpu_warn = 0
        self._last_mem_warn = 0

        self._timer = QTimer(self)
        self._timer.setInterval(2500)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _tick(self) -> None:
        snap = collect_snapshot()
        now = int(time.time())

        if snap.cpu.percent >= self._cpu_warn and (now - self._last_cpu_warn) >= self._cooldown:
            self._last_cpu_warn = now
            self._notifications.warning("High CPU usage", f"CPU is at {snap.cpu.percent:.0f}%")

        if snap.memory.percent >= self._mem_warn and (now - self._last_mem_warn) >= self._cooldown:
            self._last_mem_warn = now
            self._notifications.warning("High memory usage", f"Memory is at {snap.memory.percent:.0f}%")

