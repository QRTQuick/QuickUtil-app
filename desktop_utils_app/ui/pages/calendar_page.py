from __future__ import annotations

from datetime import date, datetime, timedelta

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QColor, QFont, QTextCharFormat
from PySide6.QtWidgets import (
    QCalendarWidget,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database.events import add_event, delete_event, event_days_in_month, list_events_for_day, update_event
from services.app_context import AppContext
from ui.dialogs.event_dialog import EventDialog


def _qdate_to_date(qd: QDate) -> date:
    return date(qd.year(), qd.month(), qd.day())


def _fmt_time(ts: int) -> str:
    return datetime.fromtimestamp(ts).strftime("%H:%M")


class CalendarPage(QWidget):
    def __init__(self, ctx: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._ctx = ctx

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("Calendar")
        title.setStyleSheet("font-size: 20pt; font-weight: 900;")
        subtitle = QLabel("Monthly view with local SQLite event storage.")
        subtitle.setStyleSheet("color: #94a3b8; font-size: 11pt;")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(14)

        self._cal = QCalendarWidget()
        self._cal.setGridVisible(False)
        self._cal.selectionChanged.connect(self._on_selection)
        self._cal.currentPageChanged.connect(self._on_month_changed)
        body_layout.addWidget(self._cal, 0)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        self._events = QTreeWidget()
        self._events.setColumnCount(2)
        self._events.setHeaderLabels(["Time", "Title"])
        self._events.setRootIsDecorated(False)
        self._events.setAlternatingRowColors(False)
        self._events.itemDoubleClicked.connect(lambda _item, _col: self.edit_selected())
        self._events.setMinimumWidth(520)

        btns = QWidget()
        btns_layout = QHBoxLayout(btns)
        btns_layout.setContentsMargins(0, 0, 0, 0)
        btns_layout.setSpacing(10)

        add_btn = QPushButton("Add Event")
        add_btn.setObjectName("Primary")
        add_btn.clicked.connect(self.add_event)

        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_selected)

        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(self.delete_selected)

        btns_layout.addWidget(add_btn)
        btns_layout.addWidget(edit_btn)
        btns_layout.addWidget(del_btn)
        btns_layout.addStretch(1)

        right_layout.addWidget(QLabel("Events for selected day:"))
        right_layout.addWidget(self._events, 1)
        right_layout.addWidget(btns)

        body_layout.addWidget(right, 1)
        layout.addWidget(body, 1)

        self._marker_fmt = QTextCharFormat()
        self._marker_fmt.setFontWeight(QFont.Weight.Bold)
        self._marker_fmt.setForeground(QColor("#fb7185"))

        self.refresh()

    def _on_selection(self) -> None:
        self.refresh_events()

    def _on_month_changed(self, year: int, month: int) -> None:
        self.refresh_month_markers(year, month)

    def refresh(self) -> None:
        self.refresh_month_markers(self._cal.yearShown(), self._cal.monthShown())
        self.refresh_events()

    def refresh_month_markers(self, year: int, month: int) -> None:
        # Clear formats for current month
        for day in range(1, 32):
            qd = QDate(year, month, day)
            if qd.isValid():
                self._cal.setDateTextFormat(qd, QTextCharFormat())

        days = event_days_in_month(self._ctx.db, year=year, month=month)
        for d in days:
            self._cal.setDateTextFormat(QDate(d.year, d.month, d.day), self._marker_fmt)

    def refresh_events(self) -> None:
        self._events.clear()
        selected = _qdate_to_date(self._cal.selectedDate())
        events = list_events_for_day(self._ctx.db, day=selected)

        for ev in events:
            item = QTreeWidgetItem([_fmt_time(ev.start_ts), ev.title])
            item.setData(0, Qt.ItemDataRole.UserRole, ev.id)
            if ev.notes:
                item.setToolTip(1, ev.notes)
            self._events.addTopLevelItem(item)

        self._events.resizeColumnToContents(0)

    def _selected_event_id(self) -> int | None:
        item = self._events.currentItem()
        if not item:
            return None
        ev_id = item.data(0, Qt.ItemDataRole.UserRole)
        try:
            return int(ev_id)
        except Exception:
            return None

    def add_event(self) -> None:
        selected = _qdate_to_date(self._cal.selectedDate())
        start = datetime(selected.year, selected.month, selected.day, 9, 0)
        end = start + timedelta(hours=1)

        dlg = EventDialog(title="Add Event", start=start, end=end, parent=self)
        if dlg.exec() != dlg.DialogCode.Accepted:
            return

        v = dlg.value()
        if not v["title"]:
            QMessageBox.warning(self, "Missing title", "Please enter a title for the event.")
            return

        add_event(self._ctx.db, title=v["title"], start=v["start"], end=v["end"], notes=v["notes"])
        self._ctx.notifications.info("Event created", v["title"])
        self.refresh()

    def edit_selected(self) -> None:
        ev_id = self._selected_event_id()
        if ev_id is None:
            return

        selected = _qdate_to_date(self._cal.selectedDate())
        events = list_events_for_day(self._ctx.db, day=selected)
        ev = next((e for e in events if e.id == ev_id), None)
        if not ev:
            return

        start = datetime.fromtimestamp(ev.start_ts)
        end = datetime.fromtimestamp(ev.end_ts) if ev.end_ts else None

        dlg = EventDialog(
            title="Edit Event",
            initial_title=ev.title,
            start=start,
            end=end,
            notes=ev.notes,
            parent=self,
        )
        if dlg.exec() != dlg.DialogCode.Accepted:
            return

        v = dlg.value()
        if not v["title"]:
            QMessageBox.warning(self, "Missing title", "Please enter a title for the event.")
            return

        update_event(
            self._ctx.db,
            event_id=ev_id,
            title=v["title"],
            start=v["start"],
            end=v["end"],
            notes=v["notes"],
        )
        self._ctx.notifications.info("Event updated", v["title"])
        self.refresh()

    def delete_selected(self) -> None:
        ev_id = self._selected_event_id()
        if ev_id is None:
            return

        res = QMessageBox.question(self, "Delete event?", "Delete the selected event?")
        if res != QMessageBox.StandardButton.Yes:
            return

        delete_event(self._ctx.db, event_id=ev_id)
        self._ctx.notifications.info("Event deleted", "The event was removed.")
        self.refresh()

