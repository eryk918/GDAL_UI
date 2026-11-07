# -*- coding: utf-8 -*-
from typing import Callable

from osgeo import gdal

from core.utils import json_to_html, file_filter, float_validator, parse_float
from tools.base_tool import BaseTool
from tools.nodata.ui.nodata_widget import NoDataWidget
from widgets.file_widget import insert_file_widget, SAVE_FILE


class NoDataTool(BaseTool):
    TOOL_NAME = 'NoData value'
    WIDGET_CLASS = NoDataWidget

    def setup(self) -> None:
        self.output_widget = insert_file_widget(
            self.widget.nodata_output_path_groupBox.layout(), 0, 1,
            SAVE_FILE, file_filter())
        self.widget.nodata_new_value_lineedit.setValidator(float_validator())
        self.widget.new_nodata_save_btn.clicked.connect(self.save)

    def on_file_changed(self, file_path: str) -> None:
        info = self.file_info(file_path)
        if not info or not info['nodata']:
            self.widget.nodata_text_box.setHtml('<h2>Brak wartości NoData</h2>')
            return
        self.widget.nodata_text_box.setHtml(
            json_to_html(info['nodata'], ['Band', 'Value'], ''))

    def save(self) -> None:
        input_file = self.require_input_file()
        if not input_file:
            return
        value = parse_float(self.widget.nodata_new_value_lineedit.text())
        if value is None:
            self.error('Podano nieprawidłową wartość NoData.')
            return
        if self.widget.nodata_output_path_groupBox.isChecked():
            output_file = self.require_output_file(self.output_widget.file_path)
            if not output_file:
                return

            def task(progress: Callable) -> None:
                gdal.Translate(output_file, input_file, noData=value,
                               callback=progress)

            self.execute(task, 'Zmiana wartości NoData zakończona pomyślnie.',
                         'Zmiana wartości NoData nie powiodła się.')
            return
        if not self.confirm('Czy chcesz nadpisać plik źródłowy?'):
            return

        def task(progress: Callable) -> None:
            dataset = gdal.Open(input_file, gdal.GA_Update)
            for index in range(1, dataset.RasterCount + 1):
                dataset.GetRasterBand(index).SetNoDataValue(value)
                progress(index / dataset.RasterCount, '', None)
            dataset.FlushCache()
            dataset = None

        _, error = self.execute(
            task, 'Zmiana wartości NoData zakończona pomyślnie.',
            'Zmiana wartości NoData nie powiodła się.')
        if not error:
            self.main_window.reload_file_info(input_file)
