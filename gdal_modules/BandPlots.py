# -*- coding: utf-8 -*-

import os.path
from abc import ABC
from typing import List, Any

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from geopandas import GeoDataFrame
from matplotlib._pylab_helpers import Gcf
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from rasterio import DatasetReader
from rasterio.plot import get_plt, show

from gdal_modules.TabPrototype import TabPrototype
from utils import load_settings, FILE_DICT_INDEXES


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, source=None, label='', file_name='',
                 vector: GeoDataFrame = None, map_preview: bool = False):
        self.fig = plt.gca().get_figure()
        if map_preview:
            Gcf.destroy_fig(self.fig)
            self.create_map_preview(source, vector)
        elif source is None:
            self.ax = plt.gca()
            self.fig = self.ax.get_figure()
        else:
            Gcf.destroy_fig(self.fig)
            self.create_hist(source, label)
        super(MplCanvas, self).__init__(self.fig)
        self.set_theme(file_name)

    def create_hist(self, source: Any, label: str) -> None:

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
            colors = [(0.16471, 0.50980, 0.85490), 'blue', 'violet', 'gold',
                      'saddlebrown']
        if arr.shape[-1] > len(colors):
            n = arr.shape[-1] - len(colors)
            colors.extend(np.ndarray.tolist(
                plt.get_cmap('Accent')(np.linspace(0, 1, n))))
        else:
            colors = colors[:arr.shape[-1]]
        self.ax = plt.gca()
        self.fig = self.ax.get_figure()
        self.ax.clear()
        self.ax.hist(arr, bins=50, color=colors, label=label, range=rng)
        self.ax.legend(loc="upper right")
        self.ax.grid(True)
        self.ax.set_xlabel('DN')
        self.ax.set_ylabel('Frequency')
        plt.axis('on')

    def create_map_preview(
            self, source: Any, vector_layer: GeoDataFrame) -> None:
        plt = get_plt()
        self.ax = plt.gca()
        self.fig = self.ax.get_figure()
        self.ax.clear()
        minx, miny, maxx, maxy = vector_layer.total_bounds
        show(source.read(), transform=source.transform, ax=self.ax)
        vector_layer.plot(ax=self.ax, color='white', alpha=.75)
        self.ax.set_xlim(minx - minx * 0.01, maxx + maxx * 0.01)
        self.ax.set_ylim(miny - miny * 0.01, maxy + maxy * 0.01)
        plt.axis('off')

    def set_theme(self, file_name: str = None) -> None:
        if load_settings().get('style') and load_settings()['style'] == 'dark':
            self.fig.patch.set_facecolor((0.25882, 0.25882, 0.25882))
            self.ax.set_title(
                f'Histogram for file {file_name}' if file_name else '',
                fontweight='bold',
                color=(0.74510, 0.74510, 0.74510)
            )
            self.ax.set_facecolor((0.25882, 0.25882, 0.25882))
            self.ax.yaxis.label.set_color((0.74510, 0.74510, 0.74510))
            self.ax.xaxis.label.set_color((0.74510, 0.74510, 0.74510))
            self.ax.tick_params(axis='x', colors=(0.74510, 0.74510, 0.74510))
            self.ax.tick_params(axis='y', colors=(0.74510, 0.74510, 0.74510))
        else:
            self.fig.patch.set_facecolor((0.98039, 0.98039, 0.98039))
            self.ax.set_title(
                f'Histogram for file {file_name}' if file_name else '',
                fontweight='bold',
                color=(0, 0, 0)
            )
            self.ax.set_facecolor((0.98039, 0.98039, 0.98039))
            self.ax.yaxis.label.set_color((0, 0, 0))
            self.ax.xaxis.label.set_color((0, 0, 0))
            self.ax.tick_params(axis='x', colors=(0, 0, 0))
            self.ax.tick_params(axis='y', colors=(0, 0, 0))


class BandPlotTab(TabPrototype, ABC):
    TOOL_NAME = 'Band plots'

    def __init__(self, main_class: callable):
        super().__init__(main_class)
        self.insert_plot_widget()
        self.dlg.file_cbbx.currentTextChanged[str].connect(
            self.fill_bands_combo)
        self.dlg.settings_btn.clicked.connect(
            lambda: self.insert_plot_widget(reload=True))

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
                    os.path.basename(self.dlg.file_cbbx.currentText()))
                if band_name else None)
            self.dlg.band_combo_plot.addItems(
                f'Band {count}' for count in range(
                    1, self.main_class.files_dict.get(file_name)
                       [FILE_DICT_INDEXES[self.TOOL_NAME]] + 1))

    def insert_plot_widget(self, *args: List[Any],
                           reload: bool = False) -> None:
        if args or reload:
            self.dlg.plot_groupBox.layout().removeItem(
                self.dlg.plot_groupBox.layout().itemAt(0))
            if reload and hasattr(self, 'backup_args'):
                args = self.backup_args
            else:
                self.backup_args = args
        self.canvas = MplCanvas(*args)
        self.dlg.plot_groupBox.layout().addWidget(self.canvas)
