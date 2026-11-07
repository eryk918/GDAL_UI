# -*- coding: utf-8 -*-
import io
import os
from contextlib import redirect_stdout
from typing import Callable, List, Tuple

from osgeo import gdal
from osgeo_utils import gdalcompare

from tools.base_tool import BaseTool
from tools.compare.ui.compare_widget import CompareWidget


class CompareTool(BaseTool):
    TOOL_NAME = 'Compare'
    WIDGET_CLASS = CompareWidget

    def setup(self) -> None:
        self.widget.compare_results_groupBox.hide()
        self.widget.compare_btn.clicked.connect(self.compare)
        self.widget.compare_second_file_cbbx.currentTextChanged.connect(
            lambda _: self.widget.compare_results_groupBox.hide())

    def on_files_loaded(self, files: List[str]) -> None:
        self.widget.compare_results_groupBox.hide()
        self.widget.compare_second_file_cbbx.clear()
        self.widget.compare_second_file_cbbx.addItems(files)

    def on_file_changed(self, file_path: str) -> None:
        self.widget.compare_results_groupBox.hide()

    def compare(self) -> None:
        self.widget.compare_results_groupBox.hide()
        base_file = self.require_input_file()
        if not base_file:
            return
        other_file = self.widget.compare_second_file_cbbx.currentText()
        if not os.path.exists(base_file) or not os.path.exists(other_file):
            self.error('Wybrane pliki nie istnieją.')
            return
        if base_file == other_file:
            self.error('Wybrano ten sam plik do porównania.')
            return

        def task(progress: Callable) -> Tuple[int, str]:
            output = io.StringIO()
            with redirect_stdout(output):
                differences = gdalcompare.compare_db(
                    gdal.Open(base_file), gdal.Open(other_file))
            return differences, output.getvalue()

        result, error = self.execute(
            task, 'Porównanie zakończone.', 'Porównanie nie powiodło się.')
        if error:
            return
        differences, report = result
        self.widget.compare_results_groupBox.show()
        self.widget.compare_textEdit.setPlainText(
            f'Base file: {base_file}\n'
            f'File to compare: {other_file}\n\n'
            f'Differences found: {differences}\n\n'
            f'{report}'
        )
