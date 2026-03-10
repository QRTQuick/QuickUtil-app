from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class WorkerSignals(QObject):
    result = Signal(object)
    error = Signal(str)
    finished = Signal()


@dataclass
class WorkerRunnable(QRunnable):
    fn: object
    args: tuple = ()
    kwargs: dict | None = None

    def __post_init__(self) -> None:
        super().__init__()
        self.signals = WorkerSignals()
        if self.kwargs is None:
            self.kwargs = {}

    @Slot()
    def run(self) -> None:
        try:
            result = self.fn(*self.args, **self.kwargs)  # type: ignore[misc]
            self.signals.result.emit(result)
        except Exception as e:  # pragma: no cover
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()

