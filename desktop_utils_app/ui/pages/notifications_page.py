from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from services.app_context import AppContext
from services.notification_service import Notification


def _fmt_ts(ts: int) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


class NotificationsPage(QWidget):
    def __init__(self, ctx: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._ctx = ctx

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        title_wrap = QWidget()
        title_layout = QVBoxLayout(title_wrap)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)

        title = QLabel("Notification Center")
        title.setStyleSheet("font-size: 20pt; font-weight: 900;")
        subtitle = QLabel("Alarms, reminders, and system warnings in one place.")
        subtitle.setStyleSheet("color: #94a3b8; font-size: 11pt;")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._ctx.notifications.clear)

        header_layout.addWidget(title_wrap, 1)
        header_layout.addWidget(clear_btn, 0, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(header)

        self._tree = QTreeWidget()
        self._tree.setColumnCount(4)
        self._tree.setHeaderLabels(["Time", "Level", "Title", "Message"])
        self._tree.setRootIsDecorated(False)
        layout.addWidget(self._tree, 1)

        self._ctx.notifications.notification_added.connect(self._on_added)
        self._ctx.notifications.cleared.connect(self._on_cleared)

        self.refresh()

    def refresh(self) -> None:
        self._tree.clear()
        for n in self._ctx.notifications.items():
            self._add_item(n, top=False)
        for col in range(4):
            self._tree.resizeColumnToContents(col)

    def _add_item(self, n: Notification, *, top: bool = True) -> None:
        item = QTreeWidgetItem([_fmt_ts(n.ts), n.level, n.title, n.message])
        if top:
            self._tree.insertTopLevelItem(0, item)
        else:
            self._tree.addTopLevelItem(item)

    def _on_added(self, n: object) -> None:
        if isinstance(n, Notification):
            self._add_item(n, top=True)
            return
        try:
            self._add_item(
                Notification(
                    ts=int(getattr(n, "ts")),
                    level=str(getattr(n, "level")),
                    title=str(getattr(n, "title")),
                    message=str(getattr(n, "message")),
                ),
                top=True,
            )
        except Exception:
            pass

    def _on_cleared(self) -> None:
        self._tree.clear()
