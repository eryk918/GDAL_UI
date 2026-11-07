# -*- coding: utf-8 -*-
import os
import re
from typing import List, Optional

from PyQt6.QtCore import Qt, QRegularExpression, QFileInfo, pyqtSignal, QDir, \
    QSize
from PyQt6.QtGui import QDropEvent, QDragEnterEvent
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QWidget, QLineEdit, \
    QToolButton, QLayout

GET_FILE = 0
GET_MULTIPLE_FILES = 1
SAVE_FILE = 2
GET_DIRECTORY = 3

PLACEHOLDERS = {
    GET_FILE: 'Wybierz plik...',
    GET_MULTIPLE_FILES: 'Wybierz pliki...',
    SAVE_FILE: 'Zapisz plik wynikowy...',
    GET_DIRECTORY: 'Wybierz katalog...'
}


class FileDropEdit(QLineEdit):
    file_dropped = pyqtSignal(str)

    def __init__(self, mode: int, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.mode = mode
        self.acceptable_extensions = []
        self.setAcceptDrops(True)
        self.setPlaceholderText(PLACEHOLDERS[mode])

    def set_filters(self, filters: str) -> None:
        self.acceptable_extensions.clear()
        if '*.*' in filters:
            return
        matches = QRegularExpression(r'\*\.(\w+)').globalMatch(filters)
        while matches.hasNext():
            match = matches.next()
            self.acceptable_extensions.append(match.captured(1).lower())

    def acceptable_paths(self, event: QDropEvent) -> List[str]:
        paths = []
        if not event.mimeData().hasUrls():
            return paths
        for url in event.mimeData().urls():
            info = QFileInfo(url.toLocalFile())
            if self.mode == GET_DIRECTORY:
                if info.isDir():
                    paths.append(info.filePath())
                elif info.isFile():
                    paths.append(info.absolutePath())
            elif info.isFile() and (
                    not self.acceptable_extensions
                    or info.suffix().lower() in self.acceptable_extensions):
                paths.append(info.filePath())
        return paths

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if self.acceptable_paths(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        paths = self.acceptable_paths(event)
        if paths:
            event.acceptProposedAction()
            self.file_dropped.emit(paths[0])


class FileWidget(QWidget):
    path_changed = pyqtSignal(str)

    def __init__(self, mode: int = GET_MULTIPLE_FILES, filters: str = '',
                 dialog_title: str = '', default_root: str = '',
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.mode = mode
        self.dialog_title = dialog_title
        self.default_root = default_root
        self._filter = ''
        self.line_edit = FileDropEdit(mode, self)
        self.line_edit.setDragEnabled(True)
        self.line_edit.setToolTip('Pełna ścieżka do pliku wraz z rozszerzeniem')
        self.line_edit.textChanged.connect(self._on_text_changed)
        self.line_edit.file_dropped.connect(self._on_file_dropped)
        self.browse_button = QToolButton(self)
        self.browse_button.setText('...')
        self.browse_button.setToolTip('Przeglądaj')
        self.browse_button.clicked.connect(self.open_dialog)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.browse_button)
        self.filter = filters

    @property
    def filter(self) -> str:
        return self._filter

    @filter.setter
    def filter(self, value: str) -> None:
        self._filter = value
        self.line_edit.set_filters(value)

    @property
    def file_path(self) -> str:
        return self.line_edit.text().strip()

    @property
    def paths(self) -> List[str]:
        text = self.file_path
        if not text:
            return []
        if '"' in text:
            return [os.path.normpath(part) for part in
                    re.findall(r'"([^"]+)"', text) if part.strip()]
        return [os.path.normpath(text)]

    def set_paths(self, paths: List[str]) -> None:
        paths = [QDir.toNativeSeparators(QDir.cleanPath(p)) for p in paths]
        if self.mode == GET_MULTIPLE_FILES and len(paths) > 1:
            self.line_edit.setText(' '.join(f'"{p}"' for p in paths))
        elif paths:
            self.line_edit.setText(paths[0])
        else:
            self.line_edit.clear()

    def _on_text_changed(self, text: str) -> None:
        paths = self.paths
        if len(paths) > 1:
            items = ''.join(f'<li>{p}</li>' for p in paths)
            self.line_edit.setToolTip(f'Wybrane pliki:<ul>{items}</ul>')
        else:
            self.line_edit.setToolTip('')
        self.path_changed.emit(text)

    def _on_file_dropped(self, path: str) -> None:
        self.set_paths([path])
        self.line_edit.selectAll()
        self.line_edit.setFocus(Qt.FocusReason.MouseFocusReason)

    def _start_directory(self) -> str:
        paths = self.paths
        if paths:
            candidate = paths[0]
            if os.path.isdir(candidate):
                return candidate
            parent = os.path.dirname(candidate)
            if os.path.isdir(parent):
                return parent
        return self.default_root or ''

    def open_dialog(self) -> None:
        start = self._start_directory()
        selected = []
        if self.mode == GET_FILE:
            name, _ = QFileDialog.getOpenFileName(
                self, self.dialog_title or 'Wybierz plik', start, self.filter)
            selected = [name] if name else []
        elif self.mode == GET_MULTIPLE_FILES:
            names, _ = QFileDialog.getOpenFileNames(
                self, self.dialog_title or 'Wybierz jeden lub więcej plików',
                start, self.filter)
            selected = names
        elif self.mode == GET_DIRECTORY:
            name = QFileDialog.getExistingDirectory(
                self, self.dialog_title or 'Wybierz katalog', start,
                QFileDialog.Option.ShowDirsOnly)
            selected = [name] if name else []
        elif self.mode == SAVE_FILE:
            name, _ = QFileDialog.getSaveFileName(
                self, self.dialog_title or 'Utwórz lub wybierz plik', start,
                self.filter)
            selected = [name] if name else []
        self.activateWindow()
        if selected:
            self.set_paths(selected)

    def minimumSizeHint(self) -> QSize:
        size = self.line_edit.minimumSizeHint()
        button = self.browse_button.minimumSizeHint()
        size.setWidth(size.width() + button.width())
        size.setHeight(max(size.height(), button.height()))
        return size


def insert_file_widget(layout: QLayout, row: int, column: int,
                       mode: int = GET_MULTIPLE_FILES, filters: str = '',
                       dialog_title: str = '') -> FileWidget:
    widget = FileWidget(mode, filters, dialog_title)
    layout.addWidget(widget, row, column)
    return widget
