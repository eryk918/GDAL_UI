# -*- coding: utf-8 -*-
import os
import sys
from abc import ABC
from typing import List, Optional

from PyQt5.QtWidgets import QMessageBox

from gdal_modules.TabPrototype import TabPrototype
from utils import APPLICATION_NAME, universal_executor


class CompareTab(TabPrototype, ABC):
    TOOL_NAME = 'Compare'
    
    def __init__(self, main_class: callable):
        super().__init__(main_class)
        self.dlg.compare_results_groupBox.hide()
        self.dlg.compare_btn.clicked.connect(self.compare_data)
        self.dlg.file_cbbx.currentTextChanged.connect(
            lambda: self.dlg.compare_results_groupBox.hide())
        self.dlg.compare_second_file_cbbx.currentTextChanged.connect(
            lambda: self.dlg.compare_results_groupBox.hide())

    def run(self, input_files: List[str],
            output_path: Optional[str] = None) -> None:
        self.execute_process(input_files, output_path)

    def execute_process(self, input_files: List[str],
                        output_path: Optional[str] = None) -> None:
        self.dlg.compare_results_groupBox.hide()
        self.dlg.compare_second_file_cbbx.clear()
        self.dlg.compare_second_file_cbbx.addItems(input_files)

    def compare_data(self) -> None:
        self.dlg.compare_results_groupBox.hide()
        lib_path = os.path.join(
            os.path.dirname(sys.executable), 'Scripts', 'gdalcompare.py')
        base_file = self.dlg.file_cbbx.currentText()
        file2compare = self.dlg.compare_second_file_cbbx.currentText()
        if not os.path.exists(lib_path):
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'GDAL library not found.',
                QMessageBox.Ok)
            return
        if not os.path.exists(base_file) or not os.path.exists(file2compare):
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'The selected files do not exist.',
                QMessageBox.Ok)
            return
        if base_file == file2compare:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'The files selected for comparison are the same.',
                QMessageBox.Ok)
            return
        std_out, _, ret_code, _ = universal_executor(
            ["python", lib_path, base_file, file2compare])
        if ret_code == 0:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'The comparison process failed.',
                QMessageBox.Ok)
            return
        self.dlg.compare_results_groupBox.show()
        self.dlg.compare_textEdit.setText(
            f'Base file: {base_file}\n'
            f'File to compare: {file2compare}\n\n'
            f'Result:\n'
            f'{std_out}'
        )
