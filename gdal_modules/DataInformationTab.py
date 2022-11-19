# -*- coding: utf-8 -*-
import json
from abc import ABC
from typing import List, Optional, Any

from gdal_modules.TabPrototype import TabPrototype
from utils import json_to_html, multiprocessing_execution


class DataInformationTab(TabPrototype, ABC):

    def __init__(self, main_class: callable):
        super().__init__(main_class)
        self.dlg.information_file_cbbx.currentTextChanged[str].connect(
            lambda text: self.show_data(text))

    def run(self, input_files: List[str],
            output_path: Optional[str] = None) -> None:
        self.execute_process(input_files, output_path)
        self.dlg.information_file_cbbx.clear()
        self.dlg.information_file_cbbx.addItems(self.files_dict.keys())

    def execute_process(self, input_files: List[str],
                        output_path: Optional[str] = None) -> None:
        self.files_dict = {}
        cmd_list = [[f'gdalinfo|-json|{file}'] for file in input_files]
        for response in multiprocessing_execution(cmd_list):
            std_out, _, code, file_path = response
            if not code:
                self.files_dict[file_path] = json.loads(std_out)

    def show_data(self, data: Any) -> None:
        if not data or data not in self.files_dict.keys():
            return
        self.dlg.information_file_webView.setHtml(
            json_to_html(self.files_dict[data]))
