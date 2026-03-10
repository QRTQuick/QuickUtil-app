from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QProgressBar, QVBoxLayout, QWidget

from ui.widgets.sparkline import SparklineWidget


class StatCard(QFrame):
    def __init__(
        self,
        title: str,
        *,
        show_progress: bool = True,
        show_sparkline: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("Card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        self._title = QLabel(title)
        self._title.setObjectName("CardTitle")

        self._value = QLabel("—")
        self._value.setObjectName("CardValue")

        self._subtitle = QLabel("")
        self._subtitle.setStyleSheet("color: #94a3b8;")
        self._subtitle.setWordWrap(True)

        layout.addWidget(self._title)
        layout.addWidget(self._value)
        layout.addWidget(self._subtitle)

        self._sparkline: SparklineWidget | None = None
        if show_sparkline:
            self._sparkline = SparklineWidget()
            layout.addWidget(self._sparkline)

        self._bar: QProgressBar | None = None
        if show_progress:
            self._bar = QProgressBar()
            self._bar.setRange(0, 100)
            self._bar.setTextVisible(True)
            self._bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self._bar)

        layout.addStretch(1)

    def set_value(self, text: str) -> None:
        self._value.setText(text)

    def set_subtitle(self, text: str) -> None:
        self._subtitle.setText(text)

    def set_progress(self, percent: float | None) -> None:
        if not self._bar:
            return
        if percent is None:
            self._bar.setValue(0)
            self._bar.setFormat("—")
            return
        p = max(0, min(100, int(round(percent))))
        self._bar.setValue(p)
        self._bar.setFormat(f"{p}%")

    def add_point(self, value: float) -> None:
        if self._sparkline:
            self._sparkline.add_point(value)

