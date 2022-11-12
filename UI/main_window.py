# -*- coding: utf-8 -*-
import os
from typing import Optional

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QWidget, QFileDialog

from utils import icon_object, raster_extensions

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

    def get_set_active_tab_name(self, idx: int = 0) -> str:
        tab_name = self.main_tab_widget.tabText(idx)
        setattr(self.main_class, 'active_tab', tab_name)
        self.main_class.tab_execution()
        return tab_name

    def setup_dialog(self) -> None:
        self.setWindowFlags(Qt.Window)
        self.setWindowIcon(icon_object)

    def connect_actions(self) -> None:
        self.select_file.clicked.connect(self.select_raster_file)
        self.main_tab_widget.currentChanged[int].connect(
            self.get_set_active_tab_name)

    def show_dialog(self) -> None:
        self.get_set_active_tab_name()
        self.show()

    def select_raster_file(self) -> None:
        paths_to_files, __ = QFileDialog.getOpenFileNames(
            self, "Select raster files: ",
            "", ' '.join([f'*.{ext}' for ext in raster_extensions]))
        files = [os.path.normpath(path) for path in paths_to_files]
        if files and files[0] != '.':
            self.main_class.connected_rasters = files
            self.select_path.setText(";".join(files))
            self.get_set_active_tab_name()
