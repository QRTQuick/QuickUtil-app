from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from database.alarms import next_alarm
from database.events import next_event
from services.app_context import AppContext
from system.collector import collect_snapshot
from ui.widgets.stat_card import StatCard


def _format_uptime(seconds: int) -> str:
    seconds = max(0, int(seconds))
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    mins, _ = divmod(rem, 60)
    if days:
        return f"{days}d {hours}h {mins}m"
    if hours:
        return f"{hours}h {mins}m"
    return f"{mins}m"


class DashboardPage(QWidget):
    def __init__(self, ctx: AppContext | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._ctx = ctx

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 20pt; font-weight: 900;")
        subtitle = QLabel("At-a-glance stats and quick actions.")
        subtitle.setStyleSheet("color: #94a3b8; font-size: 11pt;")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)

        self._cpu = StatCard("CPU", show_progress=True, show_sparkline=True)
        self._ram = StatCard("Memory", show_progress=True, show_sparkline=True)
        self._disk = StatCard("Disk", show_progress=True, show_sparkline=False)
        self._uptime = StatCard("Uptime", show_progress=False, show_sparkline=False)
        self._next_event = StatCard("Next Event", show_progress=False, show_sparkline=False)
        self._next_alarm = StatCard("Next Alarm", show_progress=False, show_sparkline=False)

        grid.addWidget(self._cpu, 0, 0)
        grid.addWidget(self._ram, 0, 1)
        grid.addWidget(self._disk, 1, 0)
        grid.addWidget(self._uptime, 1, 1)
        grid.addWidget(self._next_event, 2, 0)
        grid.addWidget(self._next_alarm, 2, 1)

        layout.addLayout(grid)

        actions = QWidget()
        actions_layout = QGridLayout(actions)
        actions_layout.setHorizontalSpacing(12)
        actions_layout.setVerticalSpacing(12)

        btn_system = QPushButton("Open System Monitor")
        btn_system.setObjectName("Primary")
        btn_system.clicked.connect(lambda _checked=False: self._navigate("system"))

        btn_calendar = QPushButton("Open Calendar")
        btn_calendar.clicked.connect(lambda _checked=False: self._navigate("calendar"))

        btn_alarms = QPushButton("Open Alarms")
        btn_alarms.clicked.connect(lambda _checked=False: self._navigate("alarms"))

        btn_wallpaper = QPushButton("Wallpaper Editor")
        btn_wallpaper.clicked.connect(lambda _checked=False: self._navigate("wallpaper"))

        actions_layout.addWidget(btn_system, 0, 0)
        actions_layout.addWidget(btn_calendar, 0, 1)
        actions_layout.addWidget(btn_alarms, 1, 0)
        actions_layout.addWidget(btn_wallpaper, 1, 1)
        layout.addWidget(actions, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(1)

        self._timer = QTimer(self)
        self._timer.setInterval(1200)
        self._timer.timeout.connect(self.refresh)
        self._timer.start()

        self.refresh()

    def _navigate(self, key: str) -> None:
        w = self.window()
        if hasattr(w, "switch_to"):
            try:
                w.switch_to(key)  # type: ignore[call-arg]
            except Exception:
                pass

    def refresh(self) -> None:
        snap = collect_snapshot()

        self._cpu.set_value(f"{snap.cpu.percent:.0f}%")
        self._cpu.set_subtitle(snap.cpu.model)
        self._cpu.set_progress(snap.cpu.percent)
        self._cpu.add_point(snap.cpu.percent)

        self._ram.set_value(f"{snap.memory.used_gb:.1f} / {snap.memory.total_gb:.1f} GB")
        self._ram.set_subtitle("RAM usage")
        self._ram.set_progress(snap.memory.percent)
        self._ram.add_point(snap.memory.percent)

        self._disk.set_value(f"{snap.disk.used_gb:.1f} / {snap.disk.total_gb:.1f} GB")
        self._disk.set_subtitle(f"Mount: {snap.disk.mount}")
        self._disk.set_progress(snap.disk.percent)

        self._uptime.set_value(_format_uptime(snap.uptime_seconds))
        self._uptime.set_subtitle(f"{snap.os_name} • {snap.hostname}")

        if self._ctx is None:
            self._next_event.set_value("—")
            self._next_event.set_subtitle("Connect calendar module to show upcoming events.")
            self._next_alarm.set_value("—")
            self._next_alarm.set_subtitle("Connect alarms module to show next alarm.")
            return

        ev = next_event(self._ctx.db, after_ts=int(datetime.now().timestamp()))
        if ev:
            when = datetime.fromtimestamp(ev.start_ts).strftime("%a %b %d • %H:%M")
            self._next_event.set_value(when)
            self._next_event.set_subtitle(ev.title)
        else:
            self._next_event.set_value("No upcoming events")
            self._next_event.set_subtitle("Add one in Calendar.")

        al = next_alarm(self._ctx.db, after_ts=int(datetime.now().timestamp()))
        if al:
            when = datetime.fromtimestamp(al.ts).strftime("%a %b %d • %H:%M")
            self._next_alarm.set_value(when)
            self._next_alarm.set_subtitle(al.label)
        else:
            self._next_alarm.set_value("No upcoming alarms")
            self._next_alarm.set_subtitle("Add one in Alarms & Reminders.")
