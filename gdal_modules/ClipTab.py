# -*- coding: utf-8 -*-
import os
from abc import ABC
from typing import List, Optional

from PyQt5.QtWidgets import QMessageBox

from CustomFileWidget import CustomFileWidget
from gdal_modules.TabPrototype import TabPrototype
from utils import APPLICATION_NAME, insert_file_widget, get_extensions, \
    universal_executor


class ClipTab(TabPrototype, ABC):

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
        self.dlg.clip_mask_widget = insert_file_widget(
            self.dlg.clip.layout(), (1, 1),
            mode=CustomFileWidget.GetFile,
            filters='; '.join([f'*.{ext}' for ext in get_extensions(False)]))
        self.dlg.clip_outdir_widget = insert_file_widget(
            self.dlg.clip.layout(), (2, 1),
            mode=CustomFileWidget.SaveFile,
            filters=';; '.join([f'*.{ext}' for ext in get_extensions()]))

    def save_data(self) -> None:
        input_file = self.dlg.clip_file_cbbx.currentText()
        output_path = self.dlg.clip_outdir_widget.filePath
        clip_path = self.dlg.clip_mask_widget.filePath
        if not output_path:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - Clip',
                'Output path not entered.',
                QMessageBox.Ok)
            return
        if not clip_path:
            QMessageBox.critical(
                self.dlg, f'{APPLICATION_NAME} - Clip',
                'Mask file path not entered.',
                QMessageBox.Ok)
            return
        elif os.path.exists(output_path):
            question = QMessageBox.warning(
                self.dlg, f'{APPLICATION_NAME} - Clip',
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
                self.dlg, f'{APPLICATION_NAME} - Clip',
                'The clip process failed.',
                QMessageBox.Ok)
            return
        QMessageBox.information(
            self.dlg, f'{APPLICATION_NAME} - Clip',
            'The clip process has been successfully completed.',
            QMessageBox.Ok)
