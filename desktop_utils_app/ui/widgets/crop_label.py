from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, Signal, Qt
from PySide6.QtWidgets import QLabel, QRubberBand, QWidget


class CropLabel(QLabel):
    crop_selected = Signal(object)  # QRect in source coordinates
    resized = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(360)
        self.setCursor(Qt.CursorShape.CrossCursor)

        self._rubber: QRubberBand | None = None
        self._origin = QPoint()
        self._crop_mode = False

        self._source_w = 1
        self._source_h = 1
        self._display_rect = QRect()

    def set_crop_mode(self, enabled: bool) -> None:
        self._crop_mode = enabled
        self.setCursor(Qt.CursorShape.CrossCursor if enabled else Qt.CursorShape.ArrowCursor)
        if not enabled and self._rubber:
            self._rubber.hide()

    def set_source_size(self, w: int, h: int) -> None:
        self._source_w = max(1, int(w))
        self._source_h = max(1, int(h))

    def _update_display_rect(self) -> None:
        pm = self.pixmap()
        if not pm:
            self._display_rect = QRect()
            return
        pw = pm.width()
        ph = pm.height()
        lw = self.width()
        lh = self.height()
        x = int((lw - pw) / 2)
        y = int((lh - ph) / 2)
        self._display_rect = QRect(x, y, pw, ph)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._update_display_rect()
        self.resized.emit()

    def setPixmap(self, pm) -> None:  # noqa: N802
        super().setPixmap(pm)
        self._update_display_rect()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if not self._crop_mode or event.button() != Qt.MouseButton.LeftButton:
            return super().mousePressEvent(event)
        if not self._display_rect.contains(event.pos()):
            return

        self._origin = event.pos()
        if self._rubber is None:
            self._rubber = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self._rubber.setGeometry(QRect(self._origin, event.pos()).normalized())
        self._rubber.show()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if not self._crop_mode or self._rubber is None:
            return super().mouseMoveEvent(event)
        rect = QRect(self._origin, event.pos()).normalized()
        rect = rect.intersected(self._display_rect)
        self._rubber.setGeometry(rect)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if not self._crop_mode or event.button() != Qt.MouseButton.LeftButton or self._rubber is None:
            return super().mouseReleaseEvent(event)

        rect = self._rubber.geometry().intersected(self._display_rect)
        self._rubber.hide()

        if rect.width() < 8 or rect.height() < 8:
            return

        # Map from label coords -> source coords.
        disp = self._display_rect
        rel_x = rect.x() - disp.x()
        rel_y = rect.y() - disp.y()

        sx = self._source_w / max(1, disp.width())
        sy = self._source_h / max(1, disp.height())

        src = QRect(
            int(rel_x * sx),
            int(rel_y * sy),
            int(rect.width() * sx),
            int(rect.height() * sy),
        )
        self.crop_selected.emit(src)
