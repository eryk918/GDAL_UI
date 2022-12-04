# -*- coding: utf-8 -*-
import os
from abc import ABC
from typing import List, Optional

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QRegExpValidator
from PyQt5.QtWidgets import QMessageBox

from CustomFileWidget import CustomFileWidget
from SimpleGdal2Tiles import SimpleGdal2Tiles
from gdal_modules.TabPrototype import TabPrototype
from utils import APPLICATION_NAME, insert_file_widget


class TilesTab(TabPrototype, ABC):

    def __init__(self, main_class: callable):
        super().__init__(main_class)
        self.setup_dialog()

    def run(self, input_files: List[str],
            output_path: Optional[str] = None) -> None:
        self.dlg.tiling_file_cbbx.clear()
        self.dlg.tiling_file_cbbx.addItems(
            [os.path.normpath(path) for path in
             self.dlg.file_widget.filePath.split('"') if os.path.exists(path)])

    def setup_dialog(self) -> None:
        self.dlg.tiling_save_btn.clicked.connect(self.save_data)
        self.dlg.tiling_outdir_lineedit = insert_file_widget(
            self.dlg.tiling_outdir_groupBox.layout(), (0, 1),
            mode=CustomFileWidget.GetDirectory)
        self.dlg.tiling_srs_lineEdit.setValidator(QIntValidator())
        self.dlg.tiling_zoom_lineEdit.setValidator(
            QRegExpValidator(QRegExp('[0-9-]{1,}')))
        self.dlg.tiling_nodata_lineEdit.setValidator(
            QDoubleValidator(-999999.9999999, 999999.9999999, 20))
        self.dlg.tiling_xyz_checkbox.hide()

    def save_data(self) -> None:
        if not self.dlg.tiling_outdir_lineedit.filePath:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - Tiling',
                'Output path not entered.',
                QMessageBox.Ok)
            return
        elif os.listdir(self.dlg.tiling_outdir_lineedit.filePath):
            question = QMessageBox.warning(
                self.dlg, f'{APPLICATION_NAME} - Tiling',
                'The directory is not empty.\n'
                'Do you want to continue?',
                QMessageBox.Yes, QMessageBox.No)
            if question == QMessageBox.No:
                return
        g2t = SimpleGdal2Tiles()
        ret_code = g2t.execute_gdal2tiles(
            self.dlg.tiling_file_cbbx.currentText(),
            self.dlg.tiling_outdir_lineedit.filePath,
            self.get_dialog_data()
        )

        if ret_code:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - Tiling',
                'The tiling process failed.',
                QMessageBox.Ok)
            return
        QMessageBox.information(
            self.dlg, f'{APPLICATION_NAME} - Tiling',
            'The tiling process has been successfully completed.',
            QMessageBox.Ok)

    def refresh_data(self) -> None:
        self.dlg.get_set_active_tab_name()

    def get_dialog_data(self):
        return {
            'nb_processes': int(os.cpu_count() / 2),
            'verbose': False,
            'resampling': self.dlg.tiling_resampling_comboBox.currentText(),
            'profile': self.dlg.tiling_profile_comboBox.currentText(),
            'tilesize': self.dlg.tiling_tilesize_spinBox.value(),
            'zoom': self.dlg.tiling_zoom_lineEdit.text()
            if self.dlg.tiling_zoom_lineEdit.text() else None,
            'srcnodata': self.dlg.tiling_nodata_lineEdit.text()
            if self.dlg.tiling_nodata_lineEdit.text() else None,
            'kml': None,
            's_srs': self.dlg.tiling_srs_lineEdit.text()
            if self.dlg.tiling_srs_lineEdit.text() else None,
            'webviewer': None,
            'title': None,
            'url': None,
            'exclude_transparent':
                self.dlg.tiling_excludetransparent_checkBox.isChecked(),
            'quiet': True,
            'resume': None,
            'xyz': self.dlg.tiling_xyz_checkbox.isChecked(),
            'tmscompatible': None
        }
