# -*- coding: utf-8 -*-
import os

from tools.base_tool import BaseTool
from tools.band_plots.ui.band_plots_widget import BandPlotsWidget
from widgets.mpl_canvas import MplCanvas


class BandPlotsTool(BaseTool):
    TOOL_NAME = 'Band plots'
    WIDGET_CLASS = BandPlotsWidget

    def setup(self) -> None:
        self.canvas = MplCanvas()
        self.widget.plot_groupBox.layout().addWidget(self.canvas)
        self.widget.band_combo_plot.currentIndexChanged.connect(self.plot)

    def on_file_changed(self, file_path: str) -> None:
        self.widget.band_combo_plot.blockSignals(True)
        self.widget.band_combo_plot.clear()
        self.widget.band_combo_plot.addItems(
            f'Band {index}' for index in
            range(1, self.band_count(file_path) + 1))
        self.widget.band_combo_plot.blockSignals(False)
        self.plot()

    def on_theme_changed(self) -> None:
        self.canvas.apply_theme()

    def plot(self) -> None:
        file_path = self.current_file
        band_index = self.widget.band_combo_plot.currentIndex() + 1
        if not file_path or band_index < 1:
            self.canvas.clear()
            return
        try:
            self.canvas.plot_histogram(
                file_path, band_index, f'Band {band_index}',
                f'Histogram dla pliku {os.path.basename(file_path)}')
        except Exception as error:
            self.canvas.clear()
            self.error(f'Nie udało się wczytać pasma.\n\n{error}')
