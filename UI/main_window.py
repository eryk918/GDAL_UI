# -*- coding: utf-8 -*-
import os

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'main_window.ui'))


class MainWindowDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(MainWindowDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.Window)

    def show_dialog(self) -> None:
        self.show()
