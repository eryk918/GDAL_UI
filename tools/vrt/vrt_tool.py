# -*- coding: utf-8 -*-
from typing import Any, Callable, Dict

from osgeo import gdal

from core.utils import regex_validator, parse_float
from tools.base_tool import BaseTool
from tools.vrt.ui.vrt_widget import VrtWidget
from widgets.file_widget import insert_file_widget, SAVE_FILE


class VrtTool(BaseTool):
    TOOL_NAME = 'VRT'
    WIDGET_CLASS = VrtWidget

    def setup(self) -> None:
        self.output_widget = insert_file_widget(
            self.widget.vrt_outdir_groupBox.layout(), 0, 1, SAVE_FILE,
            'VRT (*.vrt)')
        self.widget.vrt_user_res_x_lineEdit.setValidator(
            regex_validator(r'[0-9]+([.,][0-9]+)?'))
        self.widget.vrt_user_res_y_lineEdit.setValidator(
            regex_validator(r'[0-9]+([.,][0-9]+)?'))
        self.widget.vrt_resolution_comboBox.currentTextChanged.connect(
            lambda text: self.widget.user_res_frame.setVisible(text == 'user'))
        self.widget.user_res_frame.hide()
        self.widget.vrt_alpha_mask_checkBox.toggled.connect(
            lambda state: state and
            self.widget.vrt_separate_checkBox.setChecked(False))
        self.widget.vrt_separate_checkBox.toggled.connect(
            lambda state: state and
            self.widget.vrt_alpha_mask_checkBox.setChecked(False))
        self.widget.vrt_save_btn.clicked.connect(self.build)

    def options(self) -> Dict[str, Any]:
        resolution = self.widget.vrt_resolution_comboBox.currentText()
        options = {
            'resampleAlg': self.widget.vrt_resampling_comboBox.currentText(),
            'resolution': resolution,
            'hideNodata': self.widget.vrt_nodata_checkBox.isChecked(),
            'addAlpha': self.widget.vrt_alpha_mask_checkBox.isChecked(),
            'separate': self.widget.vrt_separate_checkBox.isChecked(),
            'allowProjectionDifference':
                self.widget.vrt_different_proj_checkBox.isChecked(),
            'targetAlignedPixels': self.widget.vrt_tap_checkBox.isChecked()
        }
        if resolution == 'user':
            options['xRes'] = parse_float(
                self.widget.vrt_user_res_x_lineEdit.text())
            options['yRes'] = parse_float(
                self.widget.vrt_user_res_y_lineEdit.text())
        return options

    def build(self) -> None:
        input_files = self.loaded_files
        if not input_files:
            self.error('Nie wybrano plików wejściowych.')
            return
        output_file = self.require_output_file(self.output_widget.file_path)
        if not output_file:
            return
        options = self.options()
        if options['resolution'] == 'user' and (
                not options['xRes'] or not options['yRes']):
            self.error('Podaj rozdzielczość X i Y.')
            return

        def task(progress: Callable) -> None:
            vrt = gdal.BuildVRT(output_file, input_files, callback=progress,
                                **options)
            vrt.FlushCache()
            vrt = None

        self.execute(task, 'Tworzenie VRT zakończone pomyślnie.',
                     'Tworzenie VRT nie powiodło się.')
