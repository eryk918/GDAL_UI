# -*- coding: utf-8 -*-
import sys
from typing import List

from PyQt6.QtWidgets import QApplication

from core.gdal_env import configure_gdal

configure_gdal()

from core.utils import get_icon
from style.style_manager import StyleManager
from tools.band_plots.band_plots_tool import BandPlotsTool
from tools.clip.clip_tool import ClipTool
from tools.compare.compare_tool import CompareTool
from tools.convert.convert_tool import ConvertTool
from tools.data_information.data_information_tool import DataInformationTool
from tools.dem.dem_tool import DemTool
from tools.merge.merge_tool import MergeTool
from tools.nodata.nodata_tool import NoDataTool
from tools.tiling.tiling_tool import TilingTool
from tools.transform.transform_tool import TransformTool
from tools.vrt.vrt_tool import VrtTool
from ui.main_window import MainWindow

TOOL_CLASSES = [
    DataInformationTool, ConvertTool, ClipTool, TransformTool, BandPlotsTool,
    NoDataTool, DemTool, TilingTool, MergeTool, CompareTool, VrtTool
]


class GdalUiApplication(QApplication):
    def __init__(self, argv: List[str]) -> None:
        super().__init__(argv)
        self.main_window = MainWindow()
        self.styler = StyleManager(self, self.main_window)
        for tool_class in TOOL_CLASSES:
            self.main_window.add_tool(tool_class(self.main_window))
        self.main_window.settings_btn.clicked.connect(self.toggle_style)
        self.styler.apply_saved_style()
        self.main_window.setWindowIcon(get_icon())
        self.main_window.show()

    def toggle_style(self, checked: bool) -> None:
        self.styler.set_style('dark' if checked else 'light')
        self.main_window.notify_theme_changed()


if __name__ == '__main__':
    application = GdalUiApplication(sys.argv)
    sys.exit(application.exec())
