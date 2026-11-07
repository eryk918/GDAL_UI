# -*- coding: utf-8 -*-
from typing import Any, Callable, Dict

from osgeo import gdal

from core.utils import file_filter, float_validator, int_validator, \
    parse_float
from tools.base_tool import BaseTool
from tools.transform.ui.transform_widget import TransformWidget
from widgets.file_widget import insert_file_widget, SAVE_FILE


class TransformTool(BaseTool):
    TOOL_NAME = 'Transform'
    WIDGET_CLASS = TransformWidget

    def setup(self) -> None:
        self.output_widget = insert_file_widget(
            self.widget.transform_outfile_groupBox.layout(), 0, 1,
            SAVE_FILE, file_filter())
        self.widget.transform_nodata_lineEdit.setValidator(float_validator())
        self.widget.transform_source_coord_lineEdit.setValidator(
            int_validator(1))
        self.widget.transform_target_coord_lineEdit.setValidator(
            int_validator(1))
        self.widget.transform_save_btn.clicked.connect(self.transform)

    def options(self) -> Dict[str, Any]:
        options = {
            'outputType': gdal.GetDataTypeByName(
                self.widget.transform_output_data_type_cbbx.currentText()),
            'workingType': gdal.GetDataTypeByName(
                self.widget.transform_source_data_type_cbbx.currentText()),
            'resampleAlg': self.widget.transform_resampling_cbbx.currentText()
        }
        source_srs = self.widget.transform_source_coord_lineEdit.text()
        target_srs = self.widget.transform_target_coord_lineEdit.text()
        nodata = parse_float(self.widget.transform_nodata_lineEdit.text())
        if source_srs:
            options['srcSRS'] = f'EPSG:{source_srs}'
        if target_srs:
            options['dstSRS'] = f'EPSG:{target_srs}'
        if nodata is not None:
            options['dstNodata'] = nodata
        return options

    def transform(self) -> None:
        input_file = self.require_input_file()
        if not input_file:
            return
        output_file = self.require_output_file(self.output_widget.file_path)
        if not output_file:
            return
        options = self.options()

        def task(progress: Callable) -> None:
            gdal.Warp(output_file, input_file, callback=progress, **options)

        self.execute(task, 'Transformacja zakończona pomyślnie.',
                     'Transformacja nie powiodła się.')
