# -*- coding: utf-8 -*-
import os
import sys
from abc import ABC
from typing import List, Optional

from PyQt5.QtWidgets import QMessageBox

from CustomFileWidget import CustomFileWidget
from gdal_modules.TabPrototype import TabPrototype
from utils import insert_file_widget, get_extensions, APPLICATION_NAME
if os.path.exists(os.path.join(os.path.dirname(sys.executable), 'Scripts')):
    sys.path.append(os.path.join(os.path.dirname(sys.executable), 'Scripts'))
import gdal_merge as gm


class MergeTilesTab(TabPrototype, ABC):

    TOOL_NAME = 'Merge Rasters'

    def __init__(self, main_class: callable):
        super().__init__(main_class)
        self.dlg.outfile_widget = insert_file_widget(
            self.dlg.merge_outfile_groupBox.layout(), (0, 1),
            mode=CustomFileWidget.SaveFile,
            filters=';; '.join([f'*.{ext}' for ext in get_extensions()]))
        self.dlg.merge_save_btn.clicked.connect(self.merge_rasters)

    def run(self, input_files: List[str],
            output_path: Optional[str] = None) -> None:
        self.execute_process(input_files, output_path)

    def execute_process(self, input_files: List[str],
                        output_path: Optional[str] = None) -> None:
        self.input_files = input_files

    def merge_rasters(self) -> None:
        output_file = self.dlg.outfile_widget.filePath

        if not hasattr(self, 'input_files') or not self.input_files:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'No input file selected.',
                QMessageBox.Ok)
            return
        if not output_file:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'No output file selected.',
                QMessageBox.Ok)
            return
        if os.path.exists(output_file):
            question = QMessageBox.warning(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'A file with this output path exists.\n'
                'Do you want to overwrite it?',
                QMessageBox.Yes, QMessageBox.No)
            if question == QMessageBox.No:
                return
        try:
            gm.main(['', *self.cmd_parameters(), '-o', output_file, *self.input_files])
        except SystemExit:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                f'Merging failed.', QMessageBox.Ok)
            return
        QMessageBox.information(
            self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
            f'File generation succeeded.', QMessageBox.Ok)

    def cmd_parameters(self) -> List[str]:
        params = ['-ps', self.dlg.pixel_x_lineEdit.text(), self.dlg.pixel_y_lineEdit.text()] \
            if all((self.dlg.pixel_x_lineEdit.text(), self.dlg.pixel_y_lineEdit.text())) else []
        if self.dlg.merge_nodata_lineEdit.text():
            params.extend(['-a_nodata', self.dlg.merge_nodata_lineEdit.text()])
        if self.dlg.separate_checkBox.isChecked():
            params.append('-separate')
        return params
