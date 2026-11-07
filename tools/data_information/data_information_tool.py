# -*- coding: utf-8 -*-
from core.utils import json_to_html
from tools.base_tool import BaseTool
from tools.data_information.ui.data_information_widget import \
    DataInformationWidget


class DataInformationTool(BaseTool):
    TOOL_NAME = 'Data information'
    WIDGET_CLASS = DataInformationWidget

    def on_file_changed(self, file_path: str) -> None:
        info = self.file_info(file_path)
        if not info:
            self.widget.information_text_browser.clear()
            return
        self.widget.information_text_browser.setHtml(
            json_to_html(info['info']))
