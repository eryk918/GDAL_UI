# -*- coding: utf-8 -*-

import json
import os.path
from abc import ABC
from typing import List, Optional, Any

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from rasterio import DatasetReader
from rasterio.plot import get_plt

from gdal_modules.TabPrototype import TabPrototype
from utils import multiprocessing_execution


class MplCanvas(FigureCanvas):

    def __init__(self, source=None, label='', file_name=''):
        if source is None:
            self.ax = plt.gca()
            self.fig = self.ax.get_figure()
        else:
            self.create_hist(source, label, file_name)
        super(MplCanvas, self).__init__(self.fig)

    def create_hist(self, source: Any, label: str,
                    file_name: str) -> None:
        plt = get_plt()
        if isinstance(source, DatasetReader):
            arr = source.read(masked=True)
        elif isinstance(source, (tuple, rasterio.Band)):
            arr = source[0].read(source[1], masked=True)
        else:
            arr = source
        rng = np.nanmin(arr), np.nanmax(arr)

        if len(arr.shape) == 2:
            arr = np.expand_dims(arr.flatten(), 0).T
            colors = ['gold']
        else:
            arr = arr.reshape(arr.shape[0], -1).T
            colors = ['red', 'green', 'blue', 'violet', 'gold', 'saddlebrown']
        if arr.shape[-1] > len(colors):
            n = arr.shape[-1] - len(colors)
            colors.extend(np.ndarray.tolist(
                plt.get_cmap('Accent')(np.linspace(0, 1, n))))
        else:
            colors = colors[:arr.shape[-1]]
        self.ax = plt.gca()
        self.fig = self.ax.get_figure()
        self.ax.clear()
        self.ax.hist(arr,
                     bins=50,
                     color=colors,
                     label=label,
                     range=rng)
        self.ax.legend(loc="upper right")
        self.ax.set_title(f'Histogram for file {file_name}', fontweight='bold')
        self.ax.grid(True)
        self.ax.set_xlabel('DN')
        self.ax.set_ylabel('Frequency')


class BandPlotTab(TabPrototype, ABC):
    def __init__(self, main_class: callable):
        super().__init__(main_class)
        self.insert_plot_widget()
        self.dlg.file_combo_plot.currentTextChanged[str].connect(
            self.fill_bands_combo)

    def run(self, input_files: List[str],
            output_path: Optional[str] = None) -> Optional[Any] or None:
        self.execute_process(input_files, output_path)
        self.dlg.file_combo_plot.clear()
        self.dlg.file_combo_plot.addItems(self.files_dict.keys())

    def execute_process(self, input_files: List[str],
                        output_path: Optional[str] = None) -> None:
        self.files_dict = {}
        cmd_list = [[f'gdalinfo|-json|{file}'] for file in input_files]
        for response in multiprocessing_execution(cmd_list):
            std_out, _, code, file_path = response
            if response and not response[2]:
                bands_list = json.loads(std_out)['bands']
                if bands_list:
                    self.files_dict[file_path] = len(bands_list)

    def fill_bands_combo(self, file_name: str) -> None:
        if file_name:
            try:
                self.dlg.band_combo_plot.disconnect()
            except TypeError:
                pass

            self.raster_file = rasterio.open(file_name)
            self.dlg.band_combo_plot.clear()
            self.dlg.band_combo_plot.currentTextChanged[str].connect(
                lambda band_name: self.insert_plot_widget(
                    self.raster_file.read([int(band_name.split(' ')[-1])]),
                    band_name,
                    os.path.basename(self.dlg.file_combo_plot.currentText()))
                if band_name else None)
            self.dlg.band_combo_plot.addItems(
                f'Band {count}' for count in range(
                    1, self.files_dict.get(file_name) + 1))

    def insert_plot_widget(self, *args: List[Any]) -> None:
        if args:
            self.dlg.plot_groupBox.layout().removeItem(
                self.dlg.plot_groupBox.layout().itemAt(0))
        self.canvas = MplCanvas(*args)
        self.dlg.plot_groupBox.layout().addWidget(self.canvas)
