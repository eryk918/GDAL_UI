# -*- coding: utf-8 -*-
import os
from abc import ABC
from typing import List

from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QMessageBox

from CustomFileWidget import CustomFileWidget
from gdal_modules.TabPrototype import TabPrototype
from utils import insert_file_widget, get_extensions, APPLICATION_NAME, \
    universal_executor, simple_int_validator


class ConvertTab(TabPrototype, ABC):
    TOOL_NAME = 'Convert'

    def __init__(self, main_class: callable):
        super().__init__(main_class)
        self.dlg.converter_out_path_lineEdit = insert_file_widget(
            self.dlg.converter_outpath_groupBox.layout(), (0, 1),
            mode=CustomFileWidget.SaveFile,
            filters=';; '.join([f'*.{ext}' for ext in get_extensions()]))
        self.dlg.converter_save_btn.clicked.connect(self.convert_file)
        self.dlg.converter_srs_lineEdit.setValidator(simple_int_validator(1))

    def convert_file(self) -> None:
        input_file = self.dlg.file_cbbx.currentText()
        output_file = self.dlg.converter_out_path_lineEdit.filePath

        if not input_file:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'No input file selected.',
                QMessageBox.Ok)
            return
        elif not output_file:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'No output file selected.',
                QMessageBox.Ok)
            return
        elif os.path.exists(output_file):
            question = QMessageBox.warning(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'A file with this output path exists.\n'
                'Do you want to overwrite it?',
                QMessageBox.Yes, QMessageBox.No)
            if question == QMessageBox.No:
                return

        _, _, ret_code, _ = \
            universal_executor(
                [cmd for cmd in
                 ['gdal_translate ', *self.cmd_parameters(), input_file,
                  output_file] if cmd],
                progress_bar=True
            )
        if ret_code:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                f'File conversion failed.',
                QMessageBox.Ok)
            return
        QMessageBox.information(
            self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
            f'File conversion succeeded.',
            QMessageBox.Ok)

    def cmd_parameters(self) -> List[str]:
        params = []
        if self.dlg.converter_data_type_comboBox.currentText() != "Same as source":
            params.extend([
                '-ot',
                self.dlg.converter_data_type_comboBox.currentText()
            ])

        if self.dlg.converter_resampling_comboBox.currentText() != "nearest (default)":
            params.extend([
                f'-r',
                self.dlg.converter_resampling_comboBox.currentText()
            ])

        if self.dlg.converter_srs_lineEdit.text():
            params.extend([
                '-a_srs',
                f'EPSG:{self.dlg.converter_srs_lineEdit.text()}'
            ])

        if self.dlg.converter_strict_checkbox.isChecked():
            params.append('-strict')
        if self.dlg.converter_recalc_stat_checkBox.isChecked():
            params.append('-stats')
        return params
