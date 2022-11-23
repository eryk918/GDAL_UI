# -*- coding: utf-8 -*-
import sys
from typing import List

from PyQt5.QtWidgets import QApplication

from UI.main_window import MainWindowDialog
from gdal_modules.BandPlots import BandPlotTab
from gdal_modules.CompareTab import CompareTab
from gdal_modules.DataInformationTab import DataInformationTab
from gdal_modules.NoDataTab import NoDataTab
from gdal_modules.TilesTab import TilesTab
from utils import get_icon


class MainDialogFunctionality(QApplication):
    def __init__(self, argv: List[str]) -> None:
        super().__init__(argv)
        self.args = argv
        self.main_dlg = MainWindowDialog(self)
        self.connected_rasters = []
        self.setup_app()
        self.run()

    def setup_app(self) -> None:
        self.setStyle('Fusion')
        self.connect_tabs()

    def connect_tabs(self) -> None:
        self.statistics_tab = DataInformationTab(self)
        self.no_data_tab = NoDataTab(self)
        self.band_plot_tab = BandPlotTab(self)
        self.tiles_tab = TilesTab(self)
        self.compare_tab = CompareTab(self)

    def tab_execution(self) -> None:
        if self.connected_rasters:
            if self.active_tab == 'Data information':
                self.statistics_tab.run(self.connected_rasters)
            elif self.active_tab == 'NoData value':
                self.no_data_tab.run(self.connected_rasters)
            elif self.active_tab == 'Tiling':
                self.tiles_tab.run(self.connected_rasters)
            elif self.active_tab == 'Band plots':
                self.band_plot_tab.run(self.connected_rasters)
            elif self.active_tab == 'Compare':
                self.compare_tab.run(self.connected_rasters)

    def run(self) -> None:
        self.main_dlg.setWindowIcon(get_icon())
        self.main_dlg.show_dialog()


main_app = MainDialogFunctionality(sys.argv)
main_app.exec()
