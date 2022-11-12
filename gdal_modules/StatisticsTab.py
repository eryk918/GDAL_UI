# -*- coding: utf-8 -*-
import json
from abc import ABC
from typing import List, Optional, Any

from gdal_modules.TabPrototype import TabPrototype
from utils import universal_executor


class StatisticsTab(TabPrototype, ABC):

    def run(self, input_files: List[str],
            output_path: Optional[str] = None) -> None:
        data = self.execute_process(input_files, output_path)
        self.dlg.statistics_file_cbbx.currentTextChanged[str].connect(
            lambda text: self.show_data(data[text]))
        self.dlg.statistics_file_cbbx.addItems(data.keys())

    def execute_process(self, input_files: List[str],
                        output_path: Optional[str] = None) -> Optional[Any]:
        cmd_template = ['gdalinfo', '-json']
        files_dict = {}
        for file in input_files:
            std_out, std_err, code = universal_executor([*cmd_template, file])
            if code == 0:
                files_dict[file] = json.loads(std_out)
        return files_dict

    def show_data(self, data: Any) -> None:
        self.dlg.statistics_text_box.setText(json.dumps(data))
