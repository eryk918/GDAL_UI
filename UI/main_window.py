# -*- coding: utf-8 -*-
import os
from typing import Any, Callable, Dict, List, Optional

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QWidget

from core.utils import raster_info, file_filter, show_error, error_text, \
    APPLICATION_NAME
from core.worker import run_task
from tools.base_tool import BaseTool
from widgets.file_widget import insert_file_widget, GET_MULTIPLE_FILES

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), 'main_window.ui'))


class MainWindow(QDialog, FORM_CLASS):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowType.Window)
        self.files_info = {}
        self.tools = []
        self.file_widget = insert_file_widget(
            self.load_groupBox.layout(), 0, 1, GET_MULTIPLE_FILES,
            file_filter())
        self.file_widget.path_changed.connect(self.load_files)
        self.file_cbbx.currentTextChanged.connect(self.notify_file_changed)
        self.main_tab_widget.currentChanged.connect(self.notify_activated)

    def add_tool(self, tool: BaseTool) -> None:
        self.tools.append(tool)
        self.main_tab_widget.addTab(tool.widget, tool.TOOL_NAME)

    def load_files(self, text: str) -> None:
        files = [path for path in self.file_widget.paths
                 if os.path.isfile(path)]
        if not files:
            return

        def task(progress: Callable) -> Dict[str, Any]:
            result = {}
            for index, path in enumerate(files):
                result[path] = raster_info(path)
                progress((index + 1) / len(files), '', None)
            return result

        result, error = run_task(self, task,
                                 'Wczytywanie informacji o plikach...')
        if error:
            show_error(self, APPLICATION_NAME,
                       f'Nie udało się wczytać plików.\n\n{error_text(error)}')
            return
        self.files_info = result
        self.file_cbbx.blockSignals(True)
        self.file_cbbx.clear()
        self.file_cbbx.addItems(self.files_info.keys())
        self.file_cbbx.blockSignals(False)
        for tool in self.tools:
            tool.on_files_loaded(self.loaded_files)
        self.notify_file_changed(self.file_cbbx.currentText())

    def reload_file_info(self, path: str) -> None:
        try:
            self.files_info[path] = raster_info(path)
        except Exception as error:
            show_error(self, APPLICATION_NAME,
                       f'Nie udało się odświeżyć pliku.\n\n{error_text(error)}')
            return
        if path == self.file_cbbx.currentText():
            self.notify_file_changed(path)

    def notify_file_changed(self, file_path: str) -> None:
        for tool in self.tools:
            tool.on_file_changed(file_path)

    def notify_activated(self, index: int) -> None:
        if 0 <= index < len(self.tools):
            self.tools[index].on_activated()

    def notify_theme_changed(self) -> None:
        for tool in self.tools:
            tool.on_theme_changed()

    @property
    def loaded_files(self) -> List[str]:
        return list(self.files_info.keys())
