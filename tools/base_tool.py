# -*- coding: utf-8 -*-
import os
from typing import Any, Callable, Dict, List, Optional, Tuple

from PyQt6.QtWidgets import QWidget

from core.utils import show_error, show_info, ask_question, error_text
from core.worker import run_task


class BaseTool:
    TOOL_NAME = ''
    WIDGET_CLASS = QWidget

    def __init__(self, main_window: Any) -> None:
        self.main_window = main_window
        self.widget = self.WIDGET_CLASS()
        self.setup()

    def setup(self) -> None:
        pass

    def on_files_loaded(self, files: List[str]) -> None:
        pass

    def on_file_changed(self, file_path: str) -> None:
        pass

    def on_activated(self) -> None:
        pass

    def on_theme_changed(self) -> None:
        pass

    @property
    def current_file(self) -> str:
        return self.main_window.file_cbbx.currentText()

    @property
    def loaded_files(self) -> List[str]:
        return list(self.main_window.files_info.keys())

    def file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        return self.main_window.files_info.get(file_path)

    def band_count(self, file_path: str) -> int:
        info = self.file_info(file_path)
        return info['band_count'] if info else 0

    def error(self, text: str) -> None:
        show_error(self.widget, self.TOOL_NAME, text)

    def info(self, text: str) -> None:
        show_info(self.widget, self.TOOL_NAME, text)

    def confirm(self, text: str) -> bool:
        return ask_question(self.widget, self.TOOL_NAME, text)

    def require_input_file(self) -> Optional[str]:
        if not self.current_file:
            self.error('Nie wybrano pliku wejściowego.')
            return None
        return self.current_file

    def require_output_file(self, path: str) -> Optional[str]:
        if not path:
            self.error('Nie podano ścieżki pliku wynikowego.')
            return None
        if os.path.exists(path) and not self.confirm(
                'Plik o podanej ścieżce już istnieje.\nCzy chcesz go nadpisać?'):
            return None
        return path

    def execute(self, func: Callable[[Callable], Any],
                success_text: str, failure_text: str
                ) -> Tuple[Any, Optional[Exception]]:
        result, error = run_task(self.widget, func)
        if error:
            self.error(f'{failure_text}\n\n{error_text(error)}')
        else:
            self.info(success_text)
        return result, error
