# -*- coding: utf-8 -*-
import os
from abc import ABC
from tempfile import mkstemp
from typing import List, Optional

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QMessageBox

from CustomFileWidget import CustomFileWidget
from gdal_modules.TabPrototype import TabPrototype
from utils import insert_file_widget, APPLICATION_NAME, \
    universal_executor


class VRTTab(TabPrototype, ABC):
    TOOL_NAME = 'VRT'

    def __init__(self, main_class: callable):
        super().__init__(main_class)
        self.dlg.vrt_output_path_lineEdit = insert_file_widget(
            self.dlg.vrt_outdir_groupBox.layout(), (0, 1),
            mode=CustomFileWidget.SaveFile,
            filters='*.vrt')
        self.dlg.vrt_save_btn.clicked.connect(self.build_vrt)
        self.setup_dialog()

    def setup_dialog(self) -> None:
        self.dlg.vrt_user_res_x_lineEdit.setValidator(
            QRegExpValidator(QRegExp('[0-9]{1,}')))
        self.dlg.vrt_user_res_y_lineEdit.setValidator(
            QRegExpValidator(QRegExp('[0-9]{1,}')))
        self.dlg.vrt_resolution_comboBox.currentTextChanged[str].connect(
            lambda text: self.dlg.user_res_frame.hide() if text != 'user' else self.dlg.user_res_frame.show())
        self.dlg.user_res_frame.hide()
        self.dlg.vrt_alpha_mask_checkBox.toggled.connect(
            lambda state: self.dlg.vrt_separate_checkBox.setChecked(False) if state else None)
        self.dlg.vrt_separate_checkBox.toggled.connect(
            lambda state: self.dlg.vrt_alpha_mask_checkBox.setChecked(False) if state else None)

    def create_tmp_txt_file(self) -> str:
        file_handle, tmp_file = mkstemp(suffix='.txt')
        os.close(file_handle)
        with open(tmp_file, 'w') as file:
            file.write('\n'.join([os.path.normpath(path) for path in
                                  self.dlg.file_widget.filePath.split('"') if os.path.exists(path)]))
        return tmp_file

    def build_vrt(self) -> None:
        output_file = self.dlg.vrt_output_path_lineEdit.filePath

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
        tmp_file = self.create_tmp_txt_file()
        _, _, ret_code, _ = \
            universal_executor(
                [cmd for cmd in ['gdalbuildvrt ', *self.cmd_parameters(), output_file, '-input_file_list', tmp_file,]
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
        params = [f'-r', self.dlg.vrt_resampling_comboBox.currentText(),
                  f'-resolution', self.dlg.vrt_resolution_comboBox.currentText()]

        if self.dlg.vrt_resolution_comboBox.currentText() == 'user':
            params.extend(['-tr', self.dlg.vrt_user_res_x_lineEdit.text(),
                           self.dlg.vrt_user_res_y_lineEdit.text()])
        if self.dlg.vrt_nodata_checkBox.isChecked():
            params.append('-hidenodata')
        if self.dlg.vrt_alpha_mask_checkBox.isChecked():
            params.append('-addalpha')
        if self.dlg.vrt_separate_checkBox.isChecked():
            params.append('-separate')
        if self.dlg.vrt_different_proj_checkBox.isChecked():
            params.append('-allow_projection_difference')
        if self.dlg.vrt_overwrite_checkBox.isChecked():
            params.append('-overwrite')
        return params
