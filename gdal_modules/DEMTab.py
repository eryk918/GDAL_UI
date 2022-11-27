# -*- coding: utf-8 -*-
import os
from abc import ABC
from typing import List, Optional

from PyQt5.QtWidgets import QMessageBox

from CustomFileWidget import CustomFileWidget
from gdal_modules.TabPrototype import TabPrototype
from utils import insert_file_widget, get_extensions, application_name, \
    universal_executor


class DEMTab(TabPrototype, ABC):
    modes_dict = {
        'hillshade': ['dem_mode_groupBox', 'dem_algorithm_label',
                      'dem_algorithm_comboBox',
                      'dem_hill_frame'],
        'slope': ['dem_mode_groupBox', 'dem_algorithm_label',
                  'dem_algorithm_comboBox',
                  'dem_slope_frame'],
        'aspect': ['dem_mode_groupBox', 'dem_algorithm_label',
                   'dem_algorithm_comboBox',
                   'dem_aspect_frame'],
        'color-relief': ['dem_mode_groupBox', 'dem_algorithm_label',
                         'dem_algorithm_comboBox',
                         'dem_color_frame'],
        'TRI': ['dem_mode_groupBox', 'dem_tri_algorithm_label',
                'dem_tri_algorithm_comboBox'],
        'TPI': [],
        'roughness': []
    }

    all_objects = [
        'dem_algorithm_label', 'dem_algorithm_comboBox',
        'dem_tri_algorithm_label', 'dem_tri_algorithm_comboBox',
        'dem_hill_frame', 'dem_slope_frame', 'dem_aspect_frame',
        'dem_color_frame', 'dem_mode_groupBox'
    ]

    def __init__(self, main_class: callable):
        super().__init__(main_class)
        self.show_hide_correct_objects()
        self.dlg.dem_output_path_lineEdit = insert_file_widget(
            self.dlg.dem_outdir_groupBox.layout(), (0, 1),
            mode=CustomFileWidget.SaveFile,
            filters=';; '.join([f'*.{ext}' for ext in get_extensions()]))
        self.dlg.dem_color_text_file = insert_file_widget(
            self.dlg.dem_color_frame.layout(), (4, 0),
            mode=CustomFileWidget.SaveFile,
            filters='*.txt')
        self.dlg.dem_mode_comboBox.currentTextChanged[str].connect(
            self.show_hide_correct_objects)
        self.dlg.dem_save_btn.clicked.connect(self.generate_dem)

    def run(self, input_files: List[str],
            output_path: Optional[str] = None) -> None:
        self.execute_process(input_files, output_path)
        self.show_hide_correct_objects()

    def execute_process(self, input_files: List[str],
                        output_path: Optional[str] = None) -> None:
        self.dlg.dem_file_cbbx.clear()
        self.dlg.dem_file_cbbx.addItems(input_files)

    def show_hide_correct_objects(self, mode: str = 'hillshade', ) -> None:
        for obj in self.all_objects:
            getattr(self.dlg, obj).hide()
        if mode:
            for obj in self.modes_dict[mode]:
                getattr(self.dlg, obj).show()

    def generate_dem(self) -> None:
        mode = self.dlg.dem_mode_comboBox.currentText()
        input_file = self.dlg.dem_file_cbbx.currentText()
        color_file = self.dlg.dem_color_text_file.filePath \
            if mode == 'color-relief' else ''
        output_file = self.dlg.dem_output_path_lineEdit.filePath

        if not input_file:
            QMessageBox.critical(
                self.dlg, f'{application_name} - DEM Analysis',
                'No input file selected.',
                QMessageBox.Ok)
            return
        if not output_file:
            QMessageBox.critical(
                self.dlg, f'{application_name} - DEM Analysis',
                'No output file selected.',
                QMessageBox.Ok)
            return
        if not color_file:
            if not output_file:
                QMessageBox.critical(
                    self.dlg, f'{application_name} - DEM Analysis',
                    'No color text file selected.',
                    QMessageBox.Ok)
                return
        elif os.path.exists(output_file):
            question = QMessageBox.warning(
                self.dlg, f'{application_name} - DEM Analysis',
                'A file with this output path exists.\n'
                'Do you want to overwrite it?',
                QMessageBox.Yes, QMessageBox.No)
            if question == QMessageBox.No:
                return

        _, _, ret_code, _ = \
            universal_executor(
                [cmd for cmd in ['gdaldem ', mode, input_file, color_file,
                                 output_file, *self.cmd_parameters(mode)]
                 if cmd],
                progress_bar=True
            )
        if ret_code:
            QMessageBox.critical(
                self.dlg, f'{application_name} - DEM Analysis',
                'The change of NoData value failed.',
                QMessageBox.Ok)
            return
        QMessageBox.information(
            self.dlg, f'{application_name} - DEM Analysis',
            'The change of NoData value was successful.',
            QMessageBox.Ok)

    def cmd_parameters(self, mode: str) -> List[str]:
        params = [
            f'-compute_edges'
            if self.dlg.dem_compute_edges_checkBox.isChecked() else '',
            f'-b' if self.dlg.dem_band_spinBox.value() else '',
        ]
        if mode == 'hillshade':
            params.extend([
                f'-z {self.dlg.dem_hill_z_spinBox.value()}',
                f'-s {self.dlg.dem_hill_scale_spinBox.value()}',
                f'-az {self.dlg.dem_hill_azimuth_spinBox.value()}',
                f'-alt {self.dlg.dem_hill_altitude_spinBox.value()}',
                f'-combined'
                if self.dlg.dem_hill_combined_shading_checkBox.isChecked()
                else '',
                f'-multidirectional'
                if self.dlg.dem_hill_multidirectional_checkBox.isChecked()
                else ''
            ])
        elif mode == 'slope':
            params.extend([
                f'-p'
                if self.dlg.dem_slope_percent_checkBox.isChecked()
                else '',
            ])
        elif mode == 'aspect':
            params.extend([
                f'-trigonometric'
                if self.dlg.dem_aspect_trigonometric_checkBox.isChecked()
                else '',
                f'-zero_for_flat'
                if self.dlg.dem_aspect_zero_for_flat_checkBox.isChecked()
                else '',
            ])
        elif mode == 'color-relief':
            params.extend([
                f'-alpha'
                if self.dlg.dem_color_nearest_checkBox.isChecked()
                else '',
                f'-exact_color_entry'
                if self.dlg.dem_color_exact_color_checkBox.isChecked()
                else '',
                f'-nearest_color_entry'
                if self.dlg.dem_color_alpha_checkBox.isChecked()
                else '',
            ])

        if mode in ('hillshade', 'slope', 'aspect'):
            params.extend(
                [f'-alg {self.dlg.dem_algorithm_comboBox.currentText()}'])
        elif mode == 'TRI':
            params.extend(
                [f'-alg {self.dlg.dem_tri_algorithm_comboBox.currentText()}'])
        return params
