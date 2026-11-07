# -*- coding: utf-8 -*-
import os
from typing import Optional

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), 'tiling.ui'))


class TilingWidget(QWidget, FORM_CLASS):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
