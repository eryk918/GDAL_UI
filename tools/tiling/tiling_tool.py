# -*- coding: utf-8 -*-
import os
from typing import Any, Callable, Dict, Optional, Tuple

from osgeo import gdal

from core.utils import float_validator, int_validator, regex_validator, \
    parse_float, parse_int
from tools.base_tool import BaseTool
from tools.tiling.ui.tiling_widget import TilingWidget
from widgets.file_widget import insert_file_widget, GET_DIRECTORY

TILING_SCHEMES = {
    'mercator': 'WebMercatorQuad',
    'geodetic': 'WorldCRS84Quad',
    'raster': 'raster'
}
SOURCE_VRT = '/vsimem/gdal_ui_tiling_source.vrt'


class TilingTool(BaseTool):
    TOOL_NAME = 'Tiling'
    WIDGET_CLASS = TilingWidget

    def setup(self) -> None:
        self.output_widget = insert_file_widget(
            self.widget.tiling_outdir_groupBox.layout(), 0, 1, GET_DIRECTORY)
        self.widget.tiling_srs_lineEdit.setValidator(int_validator(1))
        self.widget.tiling_zoom_lineEdit.setValidator(
            regex_validator(r'[0-9]{1,2}(-[0-9]{1,2})?'))
        self.widget.tiling_nodata_lineEdit.setValidator(float_validator())
        self.widget.tiling_save_btn.clicked.connect(self.generate)

    def zoom_range(self) -> Tuple[Optional[int], Optional[int]]:
        text = self.widget.tiling_zoom_lineEdit.text().strip()
        if not text:
            return None, None
        if '-' in text:
            low, high = text.split('-', 1)
            return parse_int(low), parse_int(high)
        single = parse_int(text)
        return single, single

    def options(self) -> Dict[str, Any]:
        options = {
            'tiling_scheme': TILING_SCHEMES[
                self.widget.tiling_profile_comboBox.currentText()],
            'resampling': self.widget.tiling_resampling_comboBox.currentText(),
            'tile_size': self.widget.tiling_tilesize_spinBox.value(),
            'skip_blank':
                self.widget.tiling_excludetransparent_checkBox.isChecked(),
            'convention': 'xyz'
            if self.widget.tiling_xyz_checkbox.isChecked() else 'tms',
            'num_threads': max(1, (os.cpu_count() or 2) // 2)
        }
        min_zoom, max_zoom = self.zoom_range()
        if min_zoom is not None:
            options['min_zoom'] = min_zoom
        if max_zoom is not None:
            options['max_zoom'] = max_zoom
        return options

    def source_options(self) -> Dict[str, Any]:
        options = {}
        srs = self.widget.tiling_srs_lineEdit.text()
        nodata = parse_float(self.widget.tiling_nodata_lineEdit.text())
        if srs:
            options['outputSRS'] = f'EPSG:{srs}'
        if nodata is not None:
            options['noData'] = nodata
        return options

    def generate(self) -> None:
        input_file = self.require_input_file()
        if not input_file:
            return
        output_dir = self.output_widget.file_path
        if not output_dir:
            self.error('Nie podano katalogu wynikowego.')
            return
        if os.path.isdir(output_dir) and os.listdir(output_dir) and \
                not self.confirm('Katalog nie jest pusty.\nCzy kontynuować?'):
            return
        options = self.options()
        source_options = self.source_options()

        def task(progress: Callable) -> None:
            source = input_file
            if source_options:
                source = gdal.Translate(SOURCE_VRT, input_file, format='VRT',
                                        **source_options)
            with gdal.Run('raster', 'tile', input=source, output=output_dir,
                          progress=progress, **options):
                pass
            if source_options:
                source = None
                gdal.Unlink(SOURCE_VRT)

        self.execute(task, 'Generowanie kafli zakończone pomyślnie.',
                     'Generowanie kafli nie powiodło się.')
