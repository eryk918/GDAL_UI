import os
import re
from typing import List

from PyQt5.QtCore import Qt, QRegularExpression, QFileInfo, pyqtSignal, QDir
from PyQt5.QtGui import QDropEvent, QDragEnterEvent, QDragLeaveEvent
from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QWidget, QLineEdit, \
    QToolButton


class QgsFileDropEdit(QLineEdit):
    fileDropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super(QgsFileDropEdit, self).__init__(parent)
        self.parent = parent
        self.setAcceptDrops(True)
        self.acceptable_extensions = []

    @property
    def dir_only(self):
        return self.dir_only

    @dir_only.setter
    def dir_only(self, value):
        self.dir_only = value

    @property
    def file_only(self):
        return self.file_only

    @file_only.setter
    def file_only(self, value):
        self.file_only = value

    @property
    def suffixFilter(self):
        return self.suffixFilter

    @suffixFilter.setter
    def suffixFilter(self, value):
        self.suffixFilter = value

    def set_filters(self, filters: str):
        self.acceptable_extensions.clear()
        if '*.*' in filters:
            return
        regex_match = QRegularExpression("\\*\\.(\\w+)").globalMatch(filters)
        while regex_match.hasNext():
            match = regex_match.next()
            if match.hasMatch():
                self.acceptable_extensions.append(match.captured(1).lower())

    def filter_acceptable_paths(self, event: QDropEvent) -> List[str]:
        raw_paths = []
        paths = []
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                local = url.toLocalFile()
                if local not in raw_paths:
                    raw_paths.append(local)
        if not event.mimeData().text() and \
                event.mimeData().text() not in raw_paths:
            raw_paths.append(event.mimeData().text())
        for path in raw_paths:
            file = QFileInfo(path)
            if self.parent.mStorageMode in [
                CustomFileWidget.GetFile,
                CustomFileWidget.GetMultipleFiles,
                CustomFileWidget.SaveFile]:
                if file.isFile() and (not self.acceptable_extensions or [
                    elem for elem in self.acceptable_extensions
                        if elem.lower() == file.suffix().lower()]):
                    paths.append(file.filePath())
            elif self.parent.mStorageMode == CustomFileWidget.GetDirectory:
                if file.isDir():
                    paths.append(file.filePath())
                elif file.isFile():
                    paths.append(file.absolutePath())
        return paths

    def acceptable_path(self, event: QDropEvent) -> str:
        paths = self.filter_acceptable_paths(event)
        if len(paths) > 1:
            return os.path.normpath(os.sep.join(re.split(r'\\|/', paths[0])))
        elif len(paths) == 1:
            return paths[0]
        else:
            return ''

    def dragEnterEvent(self, event: QDragEnterEvent):
        file_path = self.acceptable_path(event)
        if file_path:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        super(QgsFileDropEdit, self).dragLeaveEvent(event)
        event.accept()

    def dropEvent(self, event: QDropEvent):
        file_path = self.acceptable_path(event)
        if file_path:
            event.acceptProposedAction()
            self.fileDropped.emit(file_path)


class CustomFileWidget(QWidget):
    def __init__(self, parent=None, default_root=None, dialog_title=''):
        super(CustomFileWidget, self).__init__(parent)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.file_lineEdit = QgsFileDropEdit(self)
        self.file_lineEdit.setDragEnabled(True)
        self.file_lineEdit.setToolTip(
            "Full path to the file(s), including name and extension")
        self.file_lineEdit.textChanged.connect(self.textEdited)
        self.file_lineEdit.fileDropped.connect(self.fileDropped)
        main_layout.addWidget(self.file_lineEdit)
        self.browse_btn = QToolButton()
        self.browse_btn.setText('...')
        self.browse_btn.setToolTip("Browse")
        self.browse_btn.clicked.connect(self.openFileDialog)
        main_layout.addWidget(self.browse_btn)
        self.setLayout(main_layout)
        self._filePath = ''
        self._defaultRoot = default_root
        self._dialogTitle = dialog_title
        self._filter = ''
        self._options = QFileDialog.ShowDirsOnly
        self._mStorageMode = CustomFileWidget.GetMultipleFiles

    @property
    def filePath(self):
        return self._filePath

    @filePath.setter
    def filePath(self, value):
        self._filePath = value

    def splitFilePaths(self, path: str) -> List[str]:
        paths = []
        pathParts = re.split("\"\\s+\"", path)
        cleanRe = "(^\\s*\")|(\"\\s*)"
        for path_part in pathParts:
            paths.append(re.sub(cleanRe, '', path_part))
        return paths

    def setFilePath(self, path: str) -> None:
        self.file_lineEdit.setText(path)

    def setReadOnly(self, readOnly: bool):
        if self.mReadOnly != readOnly:
            self.mReadOnly = readOnly
            self.updateLayout()

    @property
    def dialogTitle(self):
        return self._dialogTitle

    @dialogTitle.setter
    def dialogTitle(self, value):
        self._dialogTitle = value

    @property
    def filter(self):
        return self._filter

    @filter.setter
    def filter(self, value):
        self._filter = value
        self.file_lineEdit.set_filters(value)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, value):
        self._options = value

    def isMultiFiles(self, path: str):
        return "\" \"" in path

    def textEdited(self, path: str):
        self._filePath = path
        if self.isMultiFiles(path):
            self.file_lineEdit.setToolTip(
                f'Selected files:<br><ul><li>{"</li><li>".join(self.splitFilePaths(path))}</li></ul><br>')
        else:
            self.file_lineEdit.setToolTip('')

    def fileDropped(self, filePath: str):
        self.setSelectedFileNames([filePath])
        self.file_lineEdit.selectAll()
        self.file_lineEdit.setFocus(Qt.MouseFocusReason)

    @property
    def defaultRoot(self):
        return self._defaultRoot

    @defaultRoot.setter
    def defaultRoot(self, value):
        self._defaultRoot = value

    @property
    def mStorageMode(self):
        return self._mStorageMode

    @mStorageMode.setter
    def mStorageMode(self, value):
        self._mStorageMode = value
        self.file_lineEdit.setStorageMode(value)

    @property
    def lineEdit(self):
        return self.file_lineEdit

    def updateLayout(self):
        self.browse_btn.setEnabled(not self.mReadOnly)
        self.file_lineEdit.setEnabled(not self.mReadOnly)

    def openFileDialog(self):
        old_path = ''
        if self._filePath and (os.path.exists(
                self._filePath) or self._mStorageMode == CustomFileWidget.SaveFile):
            old_path = self.relativePath(self._filePath, False)
        elif self._defaultRoot:
            old_path = QDir.cleanPath(self._defaultRoot)
        file_name = ''
        file_names = []
        if self._mStorageMode == CustomFileWidget.GetFile:
            title = self._dialogTitle if self._dialogTitle \
                else 'Select a file'
            file_name = QFileDialog.getOpenFileName(
                parent=self, caption=title,
                directory=QFileInfo(
                    old_path).absoluteFilePath(),
                filter=self._filter,
                options=self._options)
            if file_name:
                file_name = file_name[0]
        elif self._mStorageMode == CustomFileWidget.GetMultipleFiles:
            title = self._dialogTitle if self._dialogTitle \
                else 'Select one or more files'
            file_names = QFileDialog.getOpenFileNames(
                parent=self,
                caption=title,
                directory=QFileInfo(
                    old_path).absoluteFilePath(),
                filter=self._filter,
                options=self._options)
            if file_names:
                file_names = file_names[0]
        elif self._mStorageMode == CustomFileWidget.GetDirectory:
            title = self._dialogTitle if self._dialogTitle \
                else "Select a directory"
            file_name = QFileDialog.getExistingDirectory(
                parent=self,
                caption=title,
                directory=QFileInfo(
                    old_path).absoluteFilePath(),
                options=self._options)
            if file_name:
                file_name = file_name[0]
        elif self._mStorageMode == CustomFileWidget.SaveFile:
            title = self._dialogTitle if self._dialogTitle \
                else "Create or select a file"
            file_name = QFileDialog.getSaveFileName(
                parent=self, caption=title,
                directory=QFileInfo(
                    old_path).absoluteFilePath(),
                filter=self._filter,
                options=self._options)
            if file_name:
                file_name = file_name[0]
        self.activateWindow()
        if not file_name and not file_names:
            return
        if self._mStorageMode != CustomFileWidget.GetMultipleFiles:
            file_names = [file_name]
        for index in range(len(file_names)):
            file_names[index] = QDir.toNativeSeparators(QDir.cleanPath(
                QFileInfo(file_names[index]).absoluteFilePath()))
        self.setSelectedFileNames(file_names)

    def setSelectedFileNames(self, file_names: List[str]):
        if file_names:
            for index in range(len(file_names)):
                file_names[index] = self.relativePath(file_names[index], True)
        self.setFilePaths(file_names)

    def setFilePaths(self, file_names: List[str]):
        if not self._mStorageMode == CustomFileWidget.GetMultipleFiles:
            self.setFilePath(file_names[0])
        else:
            if len(file_names) > 1:
                self.setFilePath(f'''"{'" "'.join(file_names)}"''')
            else:
                self.setFilePath(file_names[0])

    def relativePath(self, file_path: str, remove_relative: bool):
        relative_path = QDir.toNativeSeparators(
            QDir.cleanPath(self._defaultRoot))
        if relative_path:
            return QDir.cleanPath(
                QDir(relative_path).relativeFilePath(file_path)) \
                if remove_relative else QDir.cleanPath(
                QDir(relative_path).filePath(file_path))
        return file_path

    def minimumSizeHint(self):
        size = self.file_lineEdit.minimumSizeHint()
        btn_size = self.browse_btn.minimumSizeHint()
        size.setWidth(size.width() + btn_size.width())
        size.setHeight(max(size.height(), btn_size.height()))
        return size

    GetFile = 0
    GetMultipleFiles = 1
    SaveFile = 2
    GetDirectory = 3
