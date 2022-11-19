# -*- coding: utf-8 -*-
import os
from typing import Optional

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QWidget, QFileDialog

from CustomFileWidget import CustomFileWidget
from utils import get_extensions

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'main_window.ui'))


class MainWindowDialog(QDialog, FORM_CLASS):
    def __init__(self, main_class: callable,
                 parent: Optional[QWidget] = None) -> None:
        super(MainWindowDialog, self).__init__(parent)
        self.setupUi(self)
        self.main_class = main_class
        self.setup_dialog()
        self.connect_actions()
        self.insert_file_widget()

    def insert_file_widget(self):
        self.file_widget = CustomFileWidget()
        self.file_widget.filter = f"({' '.join([f'*.{ext}' for ext in get_extensions()])})"
        self.file_widget.lineEdit.textChanged.connect(self.select_raster_file)
        self.load_groupBox.layout().addWidget(self.file_widget, 0, 1)

    def get_set_active_tab_name(self, idx: int = 0) -> str:
        tab_name = self.main_tab_widget.tabText(idx)
        setattr(self.main_class, 'active_tab', tab_name)
        self.main_class.tab_execution()
        return tab_name

    def setup_dialog(self) -> None:
        self.setWindowFlags(Qt.Window)

    def connect_actions(self) -> None:
        self.main_tab_widget.currentChanged[int].connect(
            self.get_set_active_tab_name)
        self.title_label_btn.clicked.connect(lambda: exec(self.label.text()))

    def show_dialog(self) -> None:
        self.get_set_active_tab_name()
        self.show()

    def select_raster_file(self) -> None:
        files = [os.path.normpath(path) for path in self.file_widget.filePath.split('"') if os.path.exists(path)]
        if files and files[0] != '.':
            self.main_class.connected_rasters = files
            self.main_class.tab_execution()
