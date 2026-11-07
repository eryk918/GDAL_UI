# -*- coding: utf-8 -*-
from typing import Any, Callable, Dict, List

from osgeo import gdal

from core.utils import file_filter, float_validator, int_validator, \
    parse_float
from tools.base_tool import BaseTool
from tools.merge.ui.merge_widget import MergeWidget
from widgets.file_widget import insert_file_widget, SAVE_FILE

MERGE_VRT = '/vsimem/gdal_ui_merge.vrt'


class MergeTool(BaseTool):
    TOOL_NAME = 'Merge tiles'
    WIDGET_CLASS = MergeWidget

    def setup(self) -> None:
        self.output_widget = insert_file_widget(
            self.widget.merge_outfile_groupBox.layout(), 0, 1,
            SAVE_FILE, file_filter())
        self.widget.merge_nodata_lineEdit.setValidator(float_validator())
        self.widget.pixel_x_lineEdit.setValidator(int_validator(1))
        self.widget.pixel_y_lineEdit.setValidator(int_validator(1))
        self.widget.merge_save_btn.clicked.connect(self.merge)

    def options(self) -> Dict[str, Any]:
        options = {}
        x_res = parse_float(self.widget.pixel_x_lineEdit.text())
        y_res = parse_float(self.widget.pixel_y_lineEdit.text())
        if x_res and y_res:
            options['xRes'] = x_res
            options['yRes'] = y_res
        return options

    def merge(self) -> None:
        input_files = self.loaded_files
        if not input_files:
            self.error('Nie wybrano plików wejściowych.')
            return
        output_file = self.require_output_file(self.output_widget.file_path)
        if not output_file:
            return
        options = self.options()
        nodata = parse_float(self.widget.merge_nodata_lineEdit.text())
        separate = self.widget.separate_checkBox.isChecked()

        def task(progress: Callable) -> None:
            self.run_merge(input_files, output_file, options, nodata,
                           separate, progress)

        self.execute(task, 'Łączenie rastrów zakończone pomyślnie.',
                     'Łączenie rastrów nie powiodło się.')

    @staticmethod
    def run_merge(input_files: List[str], output_file: str,
                  options: Dict[str, Any], nodata: float, separate: bool,
                  progress: Callable) -> None:
        if separate:
            vrt_options = dict(options, separate=True)
            if nodata is not None:
                vrt_options['VRTNodata'] = nodata
            vrt = gdal.BuildVRT(MERGE_VRT, input_files, **vrt_options)
            gdal.Translate(output_file, vrt, callback=progress)
            vrt = None
            gdal.Unlink(MERGE_VRT)
            return
        if nodata is not None:
            options['dstNodata'] = nodata
        gdal.Warp(output_file, input_files, callback=progress, **options)
