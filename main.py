# -*- coding: utf-8 -*-
import sys
from typing import List

from PyQt5.QtWidgets import QApplication

from UI.main_window import MainWindowDialog
from gdal_modules.BandPlots import BandPlotTab
from gdal_modules.ClipTab import ClipTab
from gdal_modules.CompareTab import CompareTab
from gdal_modules.ConvertTab import ConvertTab
from gdal_modules.DEMTab import DEMTab
from gdal_modules.DataInformationTab import DataInformationTab
from gdal_modules.MergeTilesTab import MergeTilesTab
from gdal_modules.NoDataTab import NoDataTab
from gdal_modules.TilesTab import TilesTab
from gdal_modules.TransformTab import TransformTab
from style.StyleManager import StyleManager
from utils import get_icon


class MainDialogFunctionality(QApplication):
    def __init__(self, argv: List[str]) -> None:
        super().__init__(argv)
        self.args = argv
        self.main_dlg = MainWindowDialog(self)
        self.styler = StyleManager(self, self.main_dlg)
        self.connected_rasters = []
        self.setup_app()
        self.run()

    def setup_app(self) -> None:
        self.main_dlg.settings_btn.clicked.connect(self.change_style)
        self.connect_tabs()

    def connect_tabs(self) -> None:
        self.statistics_tab = DataInformationTab(self)
        self.no_data_tab = NoDataTab(self)
        self.band_plot_tab = BandPlotTab(self)
        self.tiles_tab = TilesTab(self)
        self.compare_tab = CompareTab(self)
        self.dem_tab = DEMTab(self)
        self.clip_tab = ClipTab(self)
        self.merge_tab = MergeTilesTab(self)
        self.transform_tab = TransformTab(self)
        self.convert_tab = ConvertTab(self)

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
            elif self.active_tab == 'DEM Analysis':
                self.dem_tab.run(self.connected_rasters)
            elif self.active_tab == 'Clip':
                self.clip_tab.run(self.connected_rasters)
            elif self.active_tab == 'Merge tiles':
                self.merge_tab.run(self.connected_rasters)
            elif self.active_tab == 'Transform':
                self.transform_tab.run(self.connected_rasters)
            elif self.active_tab == 'Convert':
                self.convert_tab.run(self.connected_rasters)

    def run(self) -> None:
        self.change_style(False, True)
        self.main_dlg.setWindowIcon(get_icon())
        self.main_dlg.show_dialog()

    def change_style(self, state: bool, first_load: bool = False) -> None:
        self.styler.set_style('dark', first_load) if state \
            else self.styler.set_style('light', first_load)


main_app = MainDialogFunctionality(sys.argv)
main_app.exec()
