from __future__ import annotations

from collections import deque

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget


class SparklineWidget(QWidget):
    def __init__(
        self,
        *,
        max_points: int = 60,
        color: str = "#e11d48",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._values: deque[float] = deque(maxlen=max_points)
        self._color = QColor(color)
        self.setFixedHeight(34)

    def add_point(self, value: float) -> None:
        self._values.append(float(value))
        self.update()

    def clear(self) -> None:
        self._values.clear()
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        if len(self._values) < 2:
            return

        w = float(self.width())
        h = float(self.height())
        pad = 2.0

        values = list(self._values)
        vmin = min(values)
        vmax = max(values)
        if vmax - vmin < 1e-6:
            vmax = vmin + 1.0

        def y(v: float) -> float:
            # higher value -> higher line (inverted y)
            t = (v - vmin) / (vmax - vmin)
            return (h - pad) - t * (h - 2 * pad)

        step = (w - 2 * pad) / max(1, (len(values) - 1))

        path = QPainterPath(QPointF(pad, y(values[0])))
        for i, v in enumerate(values[1:], start=1):
            path.lineTo(QPointF(pad + step * i, y(v)))

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        pen = QPen(self._color, 2.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(path)

