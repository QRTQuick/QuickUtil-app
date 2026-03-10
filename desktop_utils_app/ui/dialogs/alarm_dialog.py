from __future__ import annotations

from datetime import datetime, timedelta

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)


class AlarmDialog(QDialog):
    def __init__(
        self,
        *,
        title: str = "Alarm / Reminder",
        label: str = "",
        when: datetime | None = None,
        kind: str = "alarm",
        enabled: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(520)

        now = datetime.now().replace(second=0, microsecond=0)
        when = when or (now + timedelta(minutes=10))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form.setVerticalSpacing(10)

        self.label_edit = QLineEdit(label)
        self.label_edit.setPlaceholderText("e.g., Stand up and stretch")

        self.when_edit = QDateTimeEdit()
        self.when_edit.setCalendarPopup(True)
        self.when_edit.setDateTime(when)

        self.kind_combo = QComboBox()
        self.kind_combo.addItem("Alarm", "alarm")
        self.kind_combo.addItem("Reminder", "reminder")
        idx = 0 if kind == "alarm" else 1
        self.kind_combo.setCurrentIndex(idx)

        self.enabled_check = QCheckBox("Enabled")
        self.enabled_check.setChecked(enabled)

        form.addRow("Label", self.label_edit)
        form.addRow("When", self.when_edit)
        form.addRow("Type", self.kind_combo)
        form.addRow("", self.enabled_check)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Save)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def value(self) -> dict:
        label = self.label_edit.text().strip()
        when_dt = self.when_edit.dateTime().toPython()
        kind = str(self.kind_combo.currentData())
        enabled = bool(self.enabled_check.isChecked())
        return {"label": label, "when": when_dt, "kind": kind, "enabled": enabled}

