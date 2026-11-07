# -*- coding: utf-8 -*-
from typing import Callable

from osgeo import gdal

from core.utils import file_filter
from tools.base_tool import BaseTool
from tools.clip.ui.clip_widget import ClipWidget
from widgets.file_widget import insert_file_widget, GET_FILE, SAVE_FILE
from widgets.mpl_canvas import MplCanvas


class ClipTool(BaseTool):
    TOOL_NAME = 'Clip'
    WIDGET_CLASS = ClipWidget

    def setup(self) -> None:
        self.mask_widget = insert_file_widget(
            self.widget.layout(), 0, 1, GET_FILE, file_filter(False))
        self.output_widget = insert_file_widget(
            self.widget.layout(), 1, 1, SAVE_FILE, file_filter())
        self.canvas = MplCanvas()
        self.canvas.hide()
        self.widget.clip_preview_frame.layout().addWidget(self.canvas)
        self.widget.clip_btn.clicked.connect(self.save)
        self.widget.clip_preview_btn.clicked.connect(self.toggle_preview)
        self.mask_widget.path_changed.connect(lambda _: self.hide_preview())

    def on_file_changed(self, file_path: str) -> None:
        self.hide_preview()

    def on_theme_changed(self) -> None:
        self.canvas.apply_theme()

    def hide_preview(self) -> None:
        self.canvas.hide()
        self.canvas.clear()
        self.widget.clip_preview_btn.setText('Show preview')

    def toggle_preview(self) -> None:
        if not self.canvas.isHidden():
            self.hide_preview()
            return
        input_file = self.require_input_file()
        if not input_file:
            return
        mask_file = self.mask_widget.file_path
        if not mask_file:
            self.error('Nie podano ścieżki pliku maski.')
            return
        try:
            self.canvas.plot_preview(input_file, mask_file)
        except Exception as error:
            self.error(f'Nie udało się wygenerować podglądu.\n\n{error}')
            return
        self.canvas.show()
        self.widget.clip_preview_btn.setText('Hide preview')

    def save(self) -> None:
        input_file = self.require_input_file()
        if not input_file:
            return
        mask_file = self.mask_widget.file_path
        if not mask_file:
            self.error('Nie podano ścieżki pliku maski.')
            return
        output_file = self.require_output_file(self.output_widget.file_path)
        if not output_file:
            return

        def task(progress: Callable) -> None:
            gdal.Warp(output_file, input_file, cutlineDSName=mask_file,
                      cropToCutline=True, callback=progress)

        self.execute(task, 'Przycinanie zakończone pomyślnie.',
                     'Przycinanie nie powiodło się.')
