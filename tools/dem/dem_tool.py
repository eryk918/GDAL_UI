# -*- coding: utf-8 -*-
from typing import Any, Callable, Dict

from osgeo import gdal

from core.utils import file_filter
from tools.base_tool import BaseTool
from tools.dem.ui.dem_widget import DemWidget
from widgets.file_widget import insert_file_widget, GET_FILE, SAVE_FILE

MODE_OBJECTS = {
    'hillshade': ['dem_mode_groupBox', 'dem_algorithm_label',
                  'dem_algorithm_comboBox', 'dem_hill_frame'],
    'slope': ['dem_mode_groupBox', 'dem_algorithm_label',
              'dem_algorithm_comboBox', 'dem_slope_frame'],
    'aspect': ['dem_mode_groupBox', 'dem_algorithm_label',
               'dem_algorithm_comboBox', 'dem_aspect_frame'],
    'color-relief': ['dem_mode_groupBox', 'dem_color_frame'],
    'TRI': ['dem_mode_groupBox', 'dem_tri_algorithm_label',
            'dem_tri_algorithm_comboBox'],
    'TPI': [],
    'roughness': []
}
ALL_OBJECTS = [
    'dem_algorithm_label', 'dem_algorithm_comboBox',
    'dem_tri_algorithm_label', 'dem_tri_algorithm_comboBox',
    'dem_hill_frame', 'dem_slope_frame', 'dem_aspect_frame',
    'dem_color_frame', 'dem_mode_groupBox'
]


class DemTool(BaseTool):
    TOOL_NAME = 'DEM analysis'
    WIDGET_CLASS = DemWidget

    def setup(self) -> None:
        self.output_widget = insert_file_widget(
            self.widget.dem_outdir_groupBox.layout(), 0, 1,
            SAVE_FILE, file_filter())
        self.color_file_widget = insert_file_widget(
            self.widget.dem_color_frame.layout(), 4, 0, GET_FILE,
            'Pliki tekstowe (*.txt);;Wszystkie pliki (*.*)')
        self.widget.dem_mode_comboBox.currentTextChanged.connect(
            self.show_mode_objects)
        self.widget.dem_save_btn.clicked.connect(self.generate)
        self.widget.dem_hill_combined_shading_checkBox.toggled.connect(
            lambda state: state and
            self.widget.dem_hill_multidirectional_checkBox.setChecked(False))
        self.widget.dem_hill_multidirectional_checkBox.toggled.connect(
            lambda state: state and
            self.widget.dem_hill_combined_shading_checkBox.setChecked(False))
        self.widget.dem_color_nearest_checkBox.toggled.connect(
            lambda state: state and
            self.widget.dem_color_exact_color_checkBox.setChecked(False))
        self.widget.dem_color_exact_color_checkBox.toggled.connect(
            lambda state: state and
            self.widget.dem_color_nearest_checkBox.setChecked(False))
        self.show_mode_objects(self.widget.dem_mode_comboBox.currentText())

    def on_file_changed(self, file_path: str) -> None:
        self.widget.dem_band_spinBox.setMaximum(
            max(self.band_count(file_path), 1))
        self.widget.dem_band_spinBox.setValue(1)

    def show_mode_objects(self, mode: str) -> None:
        for name in ALL_OBJECTS:
            getattr(self.widget, name).hide()
        for name in MODE_OBJECTS.get(mode, []):
            getattr(self.widget, name).show()

    def options(self, mode: str) -> Dict[str, Any]:
        options = {
            'band': self.widget.dem_band_spinBox.value(),
            'computeEdges': self.widget.dem_compute_edges_checkBox.isChecked()
        }
        if mode == 'hillshade':
            options.update({
                'zFactor': self.widget.dem_hill_z_spinBox.value(),
                'azimuth': self.widget.dem_hill_azimuth_spinBox.value(),
                'altitude': self.widget.dem_hill_altitude_spinBox.value(),
                'combined':
                    self.widget.dem_hill_combined_shading_checkBox.isChecked(),
                'multiDirectional':
                    self.widget.dem_hill_multidirectional_checkBox.isChecked()
            })
        elif mode == 'slope':
            if self.widget.dem_slope_percent_checkBox.isChecked():
                options['slopeFormat'] = 'percent'
        elif mode == 'aspect':
            options.update({
                'trigonometric':
                    self.widget.dem_aspect_trigonometric_checkBox.isChecked(),
                'zeroForFlat':
                    self.widget.dem_aspect_zero_for_flat_checkBox.isChecked()
            })
        elif mode == 'color-relief':
            options['colorFilename'] = self.color_file_widget.file_path
            options['addAlpha'] = \
                self.widget.dem_color_alpha_checkBox.isChecked()
            if self.widget.dem_color_nearest_checkBox.isChecked():
                options['colorSelection'] = 'nearest_color_entry'
            elif self.widget.dem_color_exact_color_checkBox.isChecked():
                options['colorSelection'] = 'exact_color_entry'
        if mode in ('hillshade', 'slope', 'aspect'):
            options['alg'] = self.widget.dem_algorithm_comboBox.currentText()
        elif mode == 'TRI':
            options['alg'] = \
                self.widget.dem_tri_algorithm_comboBox.currentText()
        return options

    def generate(self) -> None:
        mode = self.widget.dem_mode_comboBox.currentText()
        input_file = self.require_input_file()
        if not input_file:
            return
        if mode == 'color-relief' and not self.color_file_widget.file_path:
            self.error('Nie wybrano pliku tekstowego z kolorami.')
            return
        output_file = self.require_output_file(self.output_widget.file_path)
        if not output_file:
            return
        options = self.options(mode)

        def task(progress: Callable) -> None:
            gdal.DEMProcessing(output_file, input_file, mode,
                               callback=progress, **options)

        self.execute(task, f'Generowanie ({mode}) zakończone pomyślnie.',
                     f'Generowanie ({mode}) nie powiodło się.')
