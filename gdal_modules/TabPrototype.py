# -*- coding: utf-8 -*-
from typing import List, Optional, Any

from utils import get_dialog_object


class TabPrototype:
    def __init__(self, main_class: callable):
        self.main_class = main_class
        self.dlg = get_dialog_object(self)

    def run(self, input_files: List[str],
            output_path: Optional[str] = None) -> Optional[Any] or None:
        self.execute_process(input_files, output_path)

    def set_info(self) -> Optional[Any]:
        raise NotImplementedError

    def execute_process(self, input_files: List[str],
                        output_path: Optional[str] = None) -> Optional[Any]:
        pass

    def show_data(self, data: Any) -> Optional[Any]:
        raise NotImplementedError
