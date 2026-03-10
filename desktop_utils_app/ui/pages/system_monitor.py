from __future__ import annotations

from PySide6.QtCore import QThreadPool, QTimer, Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from system.collector import collect_hardware_report, collect_snapshot
from ui.widgets.stat_card import StatCard
from ui.widgets.worker import WorkerRunnable


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


class SystemMonitorPage(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        title_wrap = QWidget()
        title_layout = QVBoxLayout(title_wrap)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)

        title = QLabel("System Monitor")
        title.setStyleSheet("font-size: 20pt; font-weight: 900;")
        subtitle = QLabel("Real-time performance + hardware summary.")
        subtitle.setStyleSheet("color: #94a3b8; font-size: 11pt;")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addWidget(title_wrap, 1)

        refresh_report = QPushButton("Refresh Report")
        refresh_report.setToolTip("Rebuild the hardware/driver report")
        refresh_report.clicked.connect(self.refresh_report)
        header_layout.addWidget(refresh_report, 0, Qt.AlignmentFlag.AlignRight)

        layout.addWidget(header)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)

        self._cpu = StatCard("CPU", show_progress=True, show_sparkline=True)
        self._gpu = StatCard("GPU", show_progress=True, show_sparkline=False)
        self._ram = StatCard("Memory", show_progress=True, show_sparkline=True)
        self._disk = StatCard("Disk", show_progress=True, show_sparkline=False)
        self._uptime = StatCard("Uptime", show_progress=False, show_sparkline=False)
        self._os = StatCard("System", show_progress=False, show_sparkline=False)

        grid.addWidget(self._cpu, 0, 0)
        grid.addWidget(self._gpu, 0, 1)
        grid.addWidget(self._ram, 1, 0)
        grid.addWidget(self._disk, 1, 1)
        grid.addWidget(self._uptime, 2, 0)
        grid.addWidget(self._os, 2, 1)

        layout.addLayout(grid)

        group = QGroupBox("Hardware & Drivers")
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(12, 12, 12, 12)
        group_layout.setSpacing(8)

        self._report = QPlainTextEdit()
        self._report.setReadOnly(True)
        self._report.setPlaceholderText("Building report…")
        group_layout.addWidget(self._report)

        layout.addWidget(group, 1)

        self._pool = QThreadPool.globalInstance()

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self.refresh)
        self._timer.start()

        self.refresh()
        self.refresh_report()

    def refresh(self) -> None:
        snap = collect_snapshot()

        self._cpu.set_value(f"{snap.cpu.percent:.0f}%")
        cpu_meta = f"{snap.cpu.model}"
        if snap.cpu.freq_mhz:
            cpu_meta = f"{cpu_meta} • {snap.cpu.freq_mhz:.0f} MHz"
        self._cpu.set_subtitle(cpu_meta)
        self._cpu.set_progress(snap.cpu.percent)
        self._cpu.add_point(snap.cpu.percent)

        if snap.gpu:
            gpu_sub = snap.gpu.name
            if snap.gpu.memory_total_mb and snap.gpu.memory_used_mb is not None:
                gpu_sub = f"{gpu_sub} • {snap.gpu.memory_used_mb:.0f}/{snap.gpu.memory_total_mb:.0f} MB"
            self._gpu.set_value(f"{(snap.gpu.load_percent or 0):.0f}%")
            self._gpu.set_subtitle(gpu_sub)
            self._gpu.set_progress(snap.gpu.load_percent or 0.0)
        else:
            self._gpu.set_value("—")
            self._gpu.set_subtitle("GPU info not available")
            self._gpu.set_progress(None)

        self._ram.set_value(f"{snap.memory.used_gb:.1f} / {snap.memory.total_gb:.1f} GB")
        self._ram.set_subtitle("RAM usage")
        self._ram.set_progress(snap.memory.percent)
        self._ram.add_point(snap.memory.percent)

        self._disk.set_value(f"{snap.disk.used_gb:.1f} / {snap.disk.total_gb:.1f} GB")
        self._disk.set_subtitle(f"Mount: {snap.disk.mount}")
        self._disk.set_progress(snap.disk.percent)

        self._uptime.set_value(_format_uptime(snap.uptime_seconds))
        self._uptime.set_subtitle("Since last boot")

        self._os.set_value(snap.os_name)
        self._os.set_subtitle(snap.hostname)

    def refresh_report(self) -> None:
        self._report.setPlainText("Building report…")
        worker = WorkerRunnable(collect_hardware_report)
        worker.signals.result.connect(lambda text: self._report.setPlainText(str(text)))
        worker.signals.error.connect(lambda msg: self._report.setPlainText(f"Report failed: {msg}"))
        self._pool.start(worker)
