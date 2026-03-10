from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database.alarms import add_alarm, delete_alarm, list_alarms, set_alarm_enabled, update_alarm
from database.models import Alarm
from services.app_context import AppContext
from ui.dialogs.alarm_dialog import AlarmDialog


def _fmt_dt(ts: int) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


class AlarmsPage(QWidget):
    def __init__(self, ctx: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self._block_item_changed = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("Alarms & Reminders")
        title.setStyleSheet("font-size: 20pt; font-weight: 900;")
        subtitle = QLabel("Schedule alarms and get desktop notifications.")
        subtitle.setStyleSheet("color: #94a3b8; font-size: 11pt;")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        self._tree = QTreeWidget()
        self._tree.setColumnCount(5)
        self._tree.setHeaderLabels(["Enabled", "When", "Type", "Label", "State"])
        self._tree.setRootIsDecorated(False)
        self._tree.itemChanged.connect(self._on_item_changed)
        self._tree.itemDoubleClicked.connect(lambda _item, _col: self.edit_selected())
        layout.addWidget(self._tree, 1)

        btns = QWidget()
        btns_layout = QHBoxLayout(btns)
        btns_layout.setContentsMargins(0, 0, 0, 0)
        btns_layout.setSpacing(10)

        add_btn = QPushButton("Add")
        add_btn.setObjectName("Primary")
        add_btn.clicked.connect(self.add_alarm)

        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_selected)

        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(self.delete_selected)

        btns_layout.addWidget(add_btn)
        btns_layout.addWidget(edit_btn)
        btns_layout.addWidget(del_btn)
        btns_layout.addStretch(1)

        layout.addWidget(btns)

        self.refresh()

    def refresh(self) -> None:
        self._tree.clear()

        alarms = list_alarms(self._ctx.db)
        self._block_item_changed = True
        try:
            for a in alarms:
                item = self._alarm_item(a)
                self._tree.addTopLevelItem(item)
        finally:
            self._block_item_changed = False

        for col in range(4):
            self._tree.resizeColumnToContents(col)

    def _alarm_item(self, a: Alarm) -> QTreeWidgetItem:
        state = "Fired" if a.fired else "Pending"
        item = QTreeWidgetItem(["", _fmt_dt(a.ts), a.kind.capitalize(), a.label, state])
        item.setData(0, Qt.ItemDataRole.UserRole, a.id)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(0, Qt.CheckState.Checked if a.enabled else Qt.CheckState.Unchecked)
        return item

    def _selected_alarm_id(self) -> int | None:
        item = self._tree.currentItem()
        if not item:
            return None
        try:
            return int(item.data(0, Qt.ItemDataRole.UserRole))
        except Exception:
            return None

    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        if self._block_item_changed or column != 0:
            return
        alarm_id = item.data(0, Qt.ItemDataRole.UserRole)
        if alarm_id is None:
            return
        enabled = item.checkState(0) == Qt.CheckState.Checked
        set_alarm_enabled(self._ctx.db, alarm_id=int(alarm_id), enabled=enabled)
        self._ctx.notifications.info("Alarm updated", "Enabled" if enabled else "Disabled")

    def add_alarm(self) -> None:
        dlg = AlarmDialog(title="Add Alarm / Reminder", parent=self)
        if dlg.exec() != dlg.DialogCode.Accepted:
            return
        v = dlg.value()
        if not v["label"]:
            QMessageBox.warning(self, "Missing label", "Please enter a label.")
            return
        add_alarm(self._ctx.db, label=v["label"], when=v["when"], kind=v["kind"], enabled=v["enabled"])
        self._ctx.notifications.info("Scheduled", v["label"])
        self.refresh()

    def edit_selected(self) -> None:
        alarm_id = self._selected_alarm_id()
        if alarm_id is None:
            return
        alarms = list_alarms(self._ctx.db)
        a = next((x for x in alarms if x.id == alarm_id), None)
        if not a:
            return

        dlg = AlarmDialog(
            title="Edit Alarm / Reminder",
            label=a.label,
            when=datetime.fromtimestamp(a.ts),
            kind=a.kind,
            enabled=a.enabled,
            parent=self,
        )
        if dlg.exec() != dlg.DialogCode.Accepted:
            return
        v = dlg.value()
        if not v["label"]:
            QMessageBox.warning(self, "Missing label", "Please enter a label.")
            return

        update_alarm(
            self._ctx.db,
            alarm_id=alarm_id,
            label=v["label"],
            when=v["when"],
            kind=v["kind"],
            enabled=v["enabled"],
        )
        self._ctx.notifications.info("Updated", v["label"])
        self.refresh()

    def delete_selected(self) -> None:
        alarm_id = self._selected_alarm_id()
        if alarm_id is None:
            return
        res = QMessageBox.question(self, "Delete alarm?", "Delete the selected alarm/reminder?")
        if res != QMessageBox.StandardButton.Yes:
            return
        delete_alarm(self._ctx.db, alarm_id=alarm_id)
        self._ctx.notifications.info("Removed", "Alarm deleted.")
        self.refresh()
