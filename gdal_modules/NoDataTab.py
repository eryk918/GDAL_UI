# -*- coding: utf-8 -*-
import os
import tempfile
import uuid
from abc import ABC
from shutil import move
from typing import Any

from PyQt5.QtWidgets import QMessageBox

from CustomFileWidget import CustomFileWidget
from gdal_modules.TabPrototype import TabPrototype
from utils import universal_executor, json_to_html, APPLICATION_NAME, \
    get_extensions, proper_is_digit, insert_file_widget, FILE_DICT_INDEXES, \
    simple_float_validator


class NoDataTab(TabPrototype, ABC):
    TOOL_NAME = 'NoData value'

    def __init__(self, main_class: callable):
        super().__init__(main_class)
        self.dlg.file_cbbx.currentTextChanged[str].connect(
            lambda text: self.show_data(text))
        self.dlg.settings_btn.clicked.connect(
            lambda: self.show_data(
                self.dlg.file_cbbx.currentText()))
        self.dlg.new_nodata_save_btn.clicked.connect(self.save_data)
        self.dlg.nodata_new_value_lineedit.setValidator(
            simple_float_validator())
        self.dlg.nodata_output_path_lineedit = insert_file_widget(
            self.dlg.nodata_output_path_groupBox.layout(), (0, 1),
            mode=CustomFileWidget.SaveFile,
            filters=';; '.join([f'*.{ext}' for ext in get_extensions()]))

    def show_data(self, data: Any) -> None:
        if not data:
            return
        elif not self.main_class.files_dict.get(data) or not \
                self.main_class.files_dict[data][
                    FILE_DICT_INDEXES[self.TOOL_NAME]]:
            self.dlg.nodata_text_box.setText('<h2>No NoData Value!<h2>')
        else:
            self.dlg.nodata_text_box.setHtml(
                json_to_html(
                    self.main_class.files_dict[data][
                        FILE_DICT_INDEXES[self.TOOL_NAME]],
                    True,
                    ['Band', 'Value'],
                    ''
                )
            )

    def save_data(self) -> None:
        no_data = self.dlg.nodata_new_value_lineedit.text()
        output_file = self.dlg.nodata_output_path_lineedit.filePath
        input_file = self.dlg.file_cbbx.currentText()
        overwrite_source = False
        if not input_file:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'No input file selected.',
                QMessageBox.Ok)
            return
        if not proper_is_digit(no_data):
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'Invalid NoData value entered.',
                QMessageBox.Ok)
            return
        if self.dlg.nodata_output_path_groupBox.isChecked():
            if not output_file:
                QMessageBox.critical(
                    self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                    'Output path not entered.',
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
        else:
            question = QMessageBox.warning(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'Do you want to overwrite the source file?',
                QMessageBox.Yes, QMessageBox.No)
            if question == QMessageBox.No:
                return
            overwrite_source = True
            output_file = input_file
            input_file = os.path.join(tempfile.gettempdir(),
                                      f'{uuid.uuid4().hex.lower()[:14]}.'
                                      f'{os.path.splitext(input_file)[-1]}')
            move(output_file, input_file)

        _, _, ret_code, _ = \
            universal_executor(
                ['gdal_translate', '-a_nodata',
                 str(proper_is_digit(no_data, True)), input_file, output_file],
                progress_bar=True
            )
        if ret_code:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'The change of NoData value failed.',
                QMessageBox.Ok)
            if overwrite_source:
                move(input_file, output_file)
            return
        QMessageBox.information(
            self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
            'The change of NoData value was successful.',
            QMessageBox.Ok)
        if overwrite_source:
            os.remove(input_file)

    def refresh_data(self) -> None:
        self.dlg.get_set_active_tab_name()
        self.show_data(self.dlg.file_cbbx.currentText())
