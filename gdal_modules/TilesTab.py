# -*- coding: utf-8 -*-
import os
from abc import ABC
from typing import List, Optional

from PyQt5.QtWidgets import QMessageBox
from osgeo_utils import gdal2tiles

from CustomFileWidget import CustomFileWidget
from gdal_modules.TabPrototype import TabPrototype
from utils import application_name, \
    insert_file_widget


class TilesTab(TabPrototype, ABC):

    def __init__(self, main_class: callable):
        super().__init__(main_class)
        self.dlg.tiling_save_btn.clicked.connect(self.save_data)
        self.dlg.tiling_outdir_lineedit = insert_file_widget(
            self.dlg.tiling_outdir_groupBox.layout(), (0, 1),
            mode=CustomFileWidget.GetDirectory)

    def run(self, input_files: List[str],
            output_path: Optional[str] = None) -> None:
        self.dlg.tiling_file_cbbx.clear()
        self.dlg.tiling_file_cbbx.addItems(
            [os.path.normpath(path) for path in
             self.dlg.file_widget.filePath.split('"') if os.path.exists(path)])

    def save_data(self) -> None:
        dialog_data = self.get_dialog_data()
        if not dialog_data['output_dir']:
            QMessageBox.critical(
                self.dlg, f'{application_name} - Tiling',
                'Output path not entered.',
                QMessageBox.Ok)
            return
        elif os.listdir(dialog_data['output_dir']):
            question = QMessageBox.warning(
                self.dlg, f'{application_name} - Tiling',
                'The directory is not empty.\n'
                'Do you want to continue?',
                QMessageBox.Yes, QMessageBox.No)
            if question == QMessageBox.No:
                return

        ret_code = gdal2tiles.main(
            [" ".join(dialog_data['options']), dialog_data['input_file'],
             dialog_data['output_dir']])

        if ret_code is None:
            QMessageBox.critical(
                self.dlg, f'{application_name} - Tiling',
                'The tiling process failed.',
                QMessageBox.Ok)
            return
        QMessageBox.information(
            self.dlg, f'{application_name} - Tiling',
            'The tiling process has been successfully completed.',
            QMessageBox.Ok)

    def refresh_data(self) -> None:
        self.dlg.get_set_active_tab_name()

    def get_dialog_data(self):
        return {
            'input_file': self.dlg.tiling_file_cbbx.currentText(),
            'output_dir': self.dlg.tiling_outdir_lineedit.filePath,
            'options': [
                f"--profile={self.dlg.tiling_profile_comboBox.currentText()}",
                f"--resampling={self.dlg.tiling_resampling_comboBox.currentText()}",
                f"--tilesize={self.dlg.tiling_tilesize_spinBox.value()}",
                f"--s_srs=EPSG:{self.dlg.tiling_srs_lineEdit.text()}" if self.dlg.tiling_srs_lineEdit.text() else '',
                "--exclude" if self.dlg.tiling_excludetransparent_checkBox.isChecked() else '',
                "--xyz" if self.dlg.tiling_xyz_checkbox.isChecked() else '',
                f"--processes={int(os.cpu_count() / 2)}"
            ]
        }
