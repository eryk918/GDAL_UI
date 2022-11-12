# -*- coding: utf-8 -*-
import sys
from typing import List

from PyQt5.QtWidgets import QApplication

from UI.main_window import MainWindowDialog
from gdal_modules.StatisticsTab import StatisticsTab
from utils import icon_object


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
        self.setWindowIcon(icon_object)
        self.connect_tabs()

    def connect_tabs(self) -> None:
        self.statistics_tab = StatisticsTab(self)

    def tab_execution(self) -> None:
        if self.connected_rasters:
            if self.active_tab == 'Statistics':
                self.statistics_tab.run(self.connected_rasters)

    def run(self) -> None:
        self.main_dlg.show_dialog()


main_app = MainDialogFunctionality(sys.argv)
main_app.exec()
