# -*- coding: utf-8 -*-
from typing import Any, Callable, Optional, Tuple

from PyQt6.QtCore import QObject, QThread, pyqtSignal, QEventLoop
from PyQt6.QtWidgets import QProgressDialog, QWidget

from core.utils import get_icon


class TaskWorker(QObject):
    progress_changed = pyqtSignal(int)
    finished = pyqtSignal(object, object)

    def __init__(self, func: Callable[[Callable], Any]) -> None:
        super().__init__()
        self.func = func

    def run(self) -> None:
        try:
            result = self.func(self.report_progress)
        except Exception as error:
            self.finished.emit(None, error)
            return
        self.finished.emit(result, None)

    def report_progress(self, complete: float, message: str,
                        data: Any) -> int:
        self.progress_changed.emit(int(complete * 100))
        return 1


def create_progress_dialog(parent: Optional[QWidget],
                           label: str) -> QProgressDialog:
    progress = QProgressDialog(parent)
    progress.setFixedWidth(500)
    progress.setWindowTitle('Proszę czekać')
    progress.setLabelText(label)
    progress.setRange(0, 100)
    progress.setValue(0)
    progress.setAutoClose(False)
    progress.setAutoReset(False)
    progress.setCancelButton(None)
    progress.setWindowIcon(get_icon())
    return progress


def run_task(parent: Optional[QWidget], func: Callable[[Callable], Any],
             label: str = 'Trwa przetwarzanie danych...'
             ) -> Tuple[Any, Optional[Exception]]:
    progress = create_progress_dialog(parent, label)
    thread = QThread()
    worker = TaskWorker(func)
    worker.moveToThread(thread)
    loop = QEventLoop()
    outcome = {}

    def on_finished(result: Any, error: Optional[Exception]) -> None:
        outcome['result'] = result
        outcome['error'] = error
        loop.quit()

    worker.progress_changed.connect(progress.setValue)
    worker.finished.connect(on_finished)
    thread.started.connect(worker.run)
    thread.start()
    progress.show()
    loop.exec()
    thread.quit()
    thread.wait()
    progress.close()
    return outcome.get('result'), outcome.get('error')
