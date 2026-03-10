from __future__ import annotations

from datetime import datetime, timedelta

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDateTimeEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)


class EventDialog(QDialog):
    def __init__(
        self,
        *,
        title: str = "Event",
        initial_title: str = "",
        start: datetime | None = None,
        end: datetime | None = None,
        notes: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(520)

        now = datetime.now().replace(second=0, microsecond=0)
        start = start or now
        end = end or (start + timedelta(hours=1))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form.setVerticalSpacing(10)

        self.title_edit = QLineEdit(initial_title)
        self.title_edit.setPlaceholderText("e.g., Team meeting")

        self.start_edit = QDateTimeEdit()
        self.start_edit.setCalendarPopup(True)
        self.start_edit.setDateTime(start)

        self.has_end = QCheckBox("End time")
        self.has_end.setChecked(True)

        self.end_edit = QDateTimeEdit()
        self.end_edit.setCalendarPopup(True)
        self.end_edit.setDateTime(end)

        self.notes_edit = QPlainTextEdit(notes or "")
        self.notes_edit.setPlaceholderText("Notes (optional)")
        self.notes_edit.setFixedHeight(130)

        self.has_end.toggled.connect(self.end_edit.setEnabled)

        form.addRow("Title", self.title_edit)
        form.addRow("Start", self.start_edit)
        form.addRow(self.has_end, self.end_edit)
        form.addRow("Notes", self.notes_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Save)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def value(self) -> dict:
        title = self.title_edit.text().strip()
        start_dt = self.start_edit.dateTime().toPython()
        end_dt = self.end_edit.dateTime().toPython() if self.has_end.isChecked() else None
        notes = self.notes_edit.toPlainText().strip() or None
        return {"title": title, "start": start_dt, "end": end_dt, "notes": notes}

