# -*- coding: utf-8 -*-
import json
from typing import List

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from osgeo import gdal, ogr

from core.settings import is_dark

DARK_BACKGROUND = (0.25882, 0.25882, 0.25882)
DARK_FOREGROUND = (0.74510, 0.74510, 0.74510)
LIGHT_BACKGROUND = (0.98039, 0.98039, 0.98039)
LIGHT_FOREGROUND = (0, 0, 0)
HISTOGRAM_COLOR = (0.16471, 0.50980, 0.85490)
PREVIEW_MAX_SIZE = 1024


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self) -> None:
        self.figure = Figure(tight_layout=True)
        self.axes = self.figure.add_subplot(111)
        super().__init__(self.figure)
        self.title = ''
        self.apply_theme()

    def clear(self) -> None:
        self.axes.clear()
        self.title = ''
        self.apply_theme()

    def plot_histogram(self, raster_path: str, band_index: int,
                       label: str, title: str) -> None:
        dataset = gdal.Open(raster_path)
        band = dataset.GetRasterBand(band_index)
        array = band.ReadAsArray().astype(float)
        nodata = band.GetNoDataValue()
        if nodata is not None:
            array = array[array != nodata]
        array = array[np.isfinite(array)].ravel()
        self.axes.clear()
        if array.size:
            self.axes.hist(array, bins=50, color=HISTOGRAM_COLOR, label=label,
                           range=(float(array.min()), float(array.max())))
            self.axes.legend(loc='upper right')
        self.axes.grid(True)
        self.axes.set_xlabel('DN')
        self.axes.set_ylabel('Frequency')
        self.axes.set_axis_on()
        self.title = title
        self.apply_theme()

    def plot_preview(self, raster_path: str, vector_path: str) -> None:
        dataset = gdal.Open(raster_path)
        width, height = dataset.RasterXSize, dataset.RasterYSize
        scale = max(width, height) / PREVIEW_MAX_SIZE
        buf_x = int(width / scale) if scale > 1 else width
        buf_y = int(height / scale) if scale > 1 else height
        bands = min(dataset.RasterCount, 3)
        array = dataset.ReadAsArray(
            buf_xsize=buf_x, buf_ysize=buf_y,
            band_list=list(range(1, bands + 1)))
        x0, dx, _, y0, _, dy = dataset.GetGeoTransform()
        extent = (x0, x0 + dx * width, y0 + dy * height, y0)
        self.axes.clear()
        self.axes.imshow(self._normalize(array), extent=extent)
        self._draw_vector(vector_path)
        self.axes.set_axis_off()
        self.title = ''
        self.apply_theme()

    @staticmethod
    def _normalize(array: np.ndarray) -> np.ndarray:
        array = array.astype(float)
        if array.ndim == 3:
            array = np.moveaxis(array, 0, -1)
            if array.shape[-1] == 2:
                array = array[..., 0]
        finite = array[np.isfinite(array)]
        if finite.size:
            low, high = np.percentile(finite, [2, 98])
            if high > low:
                array = np.clip((array - low) / (high - low), 0, 1)
        return np.nan_to_num(array)

    def _draw_vector(self, vector_path: str) -> None:
        source = ogr.Open(vector_path)
        xs, ys = [], []
        for layer in source:
            for feature in layer:
                geometry = feature.GetGeometryRef()
                if geometry is None:
                    continue
                for ring in self._rings(json.loads(geometry.ExportToJson())):
                    x = [point[0] for point in ring]
                    y = [point[1] for point in ring]
                    xs.extend(x)
                    ys.extend(y)
                    self.axes.fill(x, y, color='white', alpha=0.75)
        if xs and ys:
            pad_x = (max(xs) - min(xs)) * 0.05 or 1
            pad_y = (max(ys) - min(ys)) * 0.05 or 1
            self.axes.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
            self.axes.set_ylim(min(ys) - pad_y, max(ys) + pad_y)

    def _rings(self, geometry: dict) -> List[List[List[float]]]:
        kind = geometry.get('type')
        coordinates = geometry.get('coordinates', [])
        if kind == 'Polygon':
            return coordinates
        if kind == 'MultiPolygon':
            return [ring for polygon in coordinates for ring in polygon]
        if kind == 'LineString':
            return [coordinates]
        if kind == 'MultiLineString':
            return coordinates
        if kind == 'GeometryCollection':
            return [ring for part in geometry.get('geometries', [])
                    for ring in self._rings(part)]
        return []

    def apply_theme(self) -> None:
        background = DARK_BACKGROUND if is_dark() else LIGHT_BACKGROUND
        foreground = DARK_FOREGROUND if is_dark() else LIGHT_FOREGROUND
        self.figure.patch.set_facecolor(background)
        self.axes.set_facecolor(background)
        self.axes.set_title(self.title, fontweight='bold', color=foreground)
        self.axes.yaxis.label.set_color(foreground)
        self.axes.xaxis.label.set_color(foreground)
        self.axes.tick_params(axis='x', colors=foreground)
        self.axes.tick_params(axis='y', colors=foreground)
        for spine in self.axes.spines.values():
            spine.set_color(foreground)
        self.draw_idle()
