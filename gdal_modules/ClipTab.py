# -*- coding: utf-8 -*-
import os
from abc import ABC
from typing import List, Optional, Any

import geopandas as gpd
import rasterio
from PyQt5.QtWidgets import QMessageBox

from CustomFileWidget import CustomFileWidget
from gdal_modules.BandPlots import MplCanvas
from gdal_modules.TabPrototype import TabPrototype
from utils import APPLICATION_NAME, insert_file_widget, get_extensions, \
    universal_executor


class ClipTab(TabPrototype, ABC):
    TOOL_NAME = 'Clip'

    def __init__(self, main_class: callable):
        super().__init__(main_class)
        self.setup_dialog()

    def run(self, input_files: List[str],
            output_path: Optional[str] = None) -> None:
        self.dlg.clip_file_cbbx.clear()
        self.dlg.clip_file_cbbx.addItems(
            [os.path.normpath(path) for path in
             self.dlg.file_widget.filePath.split('"') if os.path.exists(path)])

    def setup_dialog(self) -> None:
        self.dlg.clip_btn.clicked.connect(self.save_data)
        self.dlg.clip_preview_btn.clicked.connect(self.show_preview)
        self.dlg.clip_file_cbbx.currentTextChanged[str].connect(
            self.hide_preview)
        self.dlg.clip_mask_widget = insert_file_widget(
            self.dlg.clip.layout(), (1, 1),
            mode=CustomFileWidget.GetFile,
            filters='; '.join([f'*.{ext}' for ext in get_extensions(False)]))
        self.dlg.clip_mask_widget.lineEdit.textChanged.connect(
            self.hide_preview)
        self.dlg.clip_outdir_widget = insert_file_widget(
            self.dlg.clip.layout(), (2, 1),
            mode=CustomFileWidget.SaveFile,
            filters=';; '.join([f'*.{ext}' for ext in get_extensions()]))

    def hide_preview(self) -> bool:
        if self.dlg.clip_preview_btn.text() == 'Hide preview':
            self.dlg.clip_preview_frame.layout().removeItem(
                self.dlg.clip_preview_frame.layout().itemAt(0))
            self.dlg.clip_preview_btn.setText('Show preview')
            return True

    def show_preview(self) -> None:
        if self.hide_preview():
            return
        raster_file = self.dlg.clip_file_cbbx.currentText()
        clip_path = self.dlg.clip_mask_widget.filePath
        if not raster_file:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'Raster file not entered.',
                QMessageBox.Ok)
            return
        elif not clip_path:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'Mask file path not entered.',
                QMessageBox.Ok)
            return
        self.dlg.clip_preview_btn.setText('Hide preview')
        self.insert_plot_widget(
            rasterio.open(raster_file), None, None, gpd.read_file(clip_path))

    def insert_plot_widget(self, *args: List[Any],
                           reload: bool = False) -> None:
        if args or reload:
            self.dlg.clip_preview_frame.layout().removeItem(
                self.dlg.clip_preview_frame.layout().itemAt(0))
            if reload and hasattr(self, 'backup_args'):
                args = self.backup_args
            else:
                self.backup_args = args
        self.canvas = MplCanvas(*args, map_preview=True)
        self.dlg.clip_preview_frame.layout().addWidget(self.canvas)

    def save_data(self) -> None:
        input_file = self.dlg.clip_file_cbbx.currentText()
        output_path = self.dlg.clip_outdir_widget.filePath
        clip_path = self.dlg.clip_mask_widget.filePath
        if not input_file:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'Raster file not entered.',
                QMessageBox.Ok)
            return
        if not output_path:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'Output path not entered.',
                QMessageBox.Ok)
            return
        if not clip_path:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'Mask file path not entered.',
                QMessageBox.Ok)
            return
        elif os.path.exists(output_path):
            question = QMessageBox.warning(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'File exists.\n'
                'Do you want to overwrite?',
                QMessageBox.Yes, QMessageBox.No)
            if question == QMessageBox.No:
                return

        _, _, ret_code, _ = \
            universal_executor(
                ['gdalwarp', '-overwrite', '-crop_to_cutline',
                 '-cutline', clip_path, input_file, output_path],
                progress_bar=True
            )
        if ret_code:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
                'The clip process failed.',
                QMessageBox.Ok)
            return
        QMessageBox.information(
            self.dlg, f'{APPLICATION_NAME} - {self.TOOL_NAME}',
            'The clip process has been successfully completed.',
            QMessageBox.Ok)
