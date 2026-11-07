# -*- coding: utf-8 -*-
from typing import Any, Callable, Dict

from osgeo import gdal

from core.utils import file_filter, int_validator
from tools.base_tool import BaseTool
from tools.convert.ui.convert_widget import ConvertWidget
from widgets.file_widget import insert_file_widget, SAVE_FILE


class ConvertTool(BaseTool):
    TOOL_NAME = 'Convert'
    WIDGET_CLASS = ConvertWidget

    def setup(self) -> None:
        self.output_widget = insert_file_widget(
            self.widget.converter_outpath_groupBox.layout(), 0, 1,
            SAVE_FILE, file_filter())
        self.widget.converter_srs_lineEdit.setValidator(int_validator(1))
        self.widget.converter_save_btn.clicked.connect(self.convert)

    def options(self) -> Dict[str, Any]:
        options = {
            'strict': self.widget.converter_strict_checkbox.isChecked(),
            'stats': self.widget.converter_recalc_stat_checkBox.isChecked()
        }
        data_type = self.widget.converter_data_type_comboBox.currentText()
        if data_type != 'Same as source':
            options['outputType'] = gdal.GetDataTypeByName(data_type)
        resampling = self.widget.converter_resampling_comboBox.currentText()
        if not resampling.startswith('nearest'):
            options['resampleAlg'] = resampling
        if self.widget.converter_srs_lineEdit.text():
            options['outputSRS'] = \
                f'EPSG:{self.widget.converter_srs_lineEdit.text()}'
        return options

    def convert(self) -> None:
        input_file = self.require_input_file()
        if not input_file:
            return
        output_file = self.require_output_file(self.output_widget.file_path)
        if not output_file:
            return
        options = self.options()

        def task(progress: Callable) -> None:
            gdal.Translate(output_file, input_file, callback=progress,
                           **options)

        self.execute(task, 'Konwersja pliku zakończona pomyślnie.',
                     'Konwersja pliku nie powiodła się.')
