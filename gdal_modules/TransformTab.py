# -*- coding: utf-8 -*-
import os
from abc import ABC
from typing import List, Optional

from PyQt5.QtWidgets import QMessageBox

from CustomFileWidget import CustomFileWidget
from gdal_modules.TabPrototype import TabPrototype
from utils import insert_file_widget, get_extensions, APPLICATION_NAME, \
    universal_executor


class TransformTab(TabPrototype, ABC):
    TOOL_NAME = 'Merge Rasters'

    def __init__(self, main_class: callable):
        super().__init__(main_class)
        self.dlg.transform_output_path_lineEdit = insert_file_widget(
            self.dlg.transform_outfile_groupBox.layout(), (0, 1),
            mode=CustomFileWidget.SaveFile,
            filters=';; '.join([f'*.{ext}' for ext in get_extensions()]))
        self.dlg.transform_save_btn.clicked.connect(self.generate_dem)

    def run(self, input_files: List[str],
            output_path: Optional[str] = None) -> None:
        self.execute_process(input_files, output_path)

    def execute_process(self, input_files: List[str],
                        output_path: Optional[str] = None) -> None:
        self.dlg.transform_file_cbbx.clear()
        self.dlg.transform_file_cbbx.addItems(input_files)

    def generate_dem(self) -> None:
        input_file = self.dlg.transform_file_cbbx.currentText()
        output_file = self.dlg.transform_output_path_lineEdit.filePath

        if not input_file:
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

        _, _, ret_code, _ = \
            universal_executor(
                [cmd for cmd in ['gdalwarp ', *self.cmd_parameters(), input_file, output_file,]
                 if cmd],
                progress_bar=True
            )
        if ret_code:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                f'File generation failed.',
                QMessageBox.Ok)
            return
        QMessageBox.information(
            self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
            f'File generation succeeded.',
            QMessageBox.Ok)

    def cmd_parameters(self) -> List[str]:
        params = [f'-ot', self.dlg.transform_output_data_type_cbbx.currentText(),
                  f'-wt', self.dlg.transform_source_data_type_cbbx.currentText(),
                  f'-r', self.dlg.transform_resampling_cbbx.currentText()]
        if self.dlg.transform_source_coord_lineEdit.text():
            params.extend(['-s_srs', f'EPSG:{self.dlg.transform_source_coord_lineEdit.text()}'])
        if self.dlg.transform_source_coord_lineEdit.text():
            params.extend(['-t_srs', f'EPSG:{self.dlg.transform_target_coord_lineEdit.text()}'])
        if self.dlg.transform_source_coord_lineEdit.text():
            params.extend(['-dstnodata', self.dlg.transform_nodata_lineEdit.text()])
        if self.dlg.transform_overwrite_checkBox.isChecked():
            params.append('-overwrite')
        return params
