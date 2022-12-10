# -*- coding: utf-8 -*-
from abc import ABC
from typing import Any

from gdal_modules.TabPrototype import TabPrototype
from utils import json_to_html, FILE_DICT_INDEXES


class DataInformationTab(TabPrototype, ABC):
    TOOL_NAME = 'Data information'

    def __init__(self, main_class: callable):
        super().__init__(main_class)
        self.dlg.file_cbbx.currentTextChanged[str].connect(
            lambda text: self.show_data(text))
        self.dlg.settings_btn.clicked.connect(
            lambda: self.show_data(
                self.dlg.file_cbbx.currentText()))

    def show_data(self, data: Any) -> None:
        if not data or data not in self.main_class.files_dict.keys():
            return
        self.dlg.information_file_webView.setHtml(
            json_to_html(self.main_class.files_dict[data]
                         [FILE_DICT_INDEXES[self.TOOL_NAME]]))
