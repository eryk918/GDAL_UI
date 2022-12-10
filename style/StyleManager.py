# -*- coding: utf-8 -*-
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication, QDialog

from utils import load_settings, save_settings


class StyleManager:
    def __init__(self, application: QApplication, dialog: QDialog):
        self.application = application
        self.dialog = dialog

    def set_style(self, mode: str, first_load: bool = False) -> None:
        if first_load:
            settings = load_settings()
            if settings:
                mode = settings['style']

        if mode == 'dark':
            self.set_dark_style()
            self.dialog.settings_btn.setText('🌞')
            self.dialog.settings_btn.setChecked(True)

        else:
            self.set_light_style()
            self.dialog.settings_btn.setText('🌜')
            self.dialog.settings_btn.setChecked(False)
        self.apply_theme()
        save_settings({'style': mode})

    def set_dark_style(self) -> None:
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.WindowText, QColor(180, 180, 180))
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.Light, QColor(180, 180, 180))
        dark_palette.setColor(QPalette.Midlight, QColor(90, 90, 90))
        dark_palette.setColor(QPalette.Dark, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.Text, QColor(180, 180, 180))
        dark_palette.setColor(QPalette.BrightText, QColor(180, 180, 180))
        dark_palette.setColor(QPalette.ButtonText, QColor(180, 180, 180))
        dark_palette.setColor(QPalette.Base, QColor(42, 42, 42))
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.Shadow, QColor(20, 20, 20))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(180, 180, 180))
        dark_palette.setColor(QPalette.Link, QColor(56, 252, 196))
        dark_palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipText, QColor(180, 180, 180))
        dark_palette.setColor(QPalette.LinkVisited, QColor(80, 80, 80))
        dark_palette.setColor(QPalette.Disabled, QPalette.WindowText,
                              QColor(127, 127, 127))
        dark_palette.setColor(QPalette.Disabled, QPalette.Text,
                              QColor(127, 127, 127))
        dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText,
                              QColor(127, 127, 127))
        dark_palette.setColor(QPalette.Disabled, QPalette.Highlight,
                              QColor(80, 80, 80))
        dark_palette.setColor(QPalette.Disabled, QPalette.HighlightedText,
                              QColor(127, 127, 127))
        self.dialog.title_label.setStyleSheet(
            'color:#BEBEBE; '
            'margin-left:33px; '
            'background: none;'
        )
        self.dialog.title_frame.setStyleSheet('''
            background: qlineargradient(
                    spread:reflect, x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgba(19, 0, 56, 255), 
                    stop:1 rgba(35, 61, 27, 255)
                )
        ''')
        self.application.setPalette(dark_palette)

    def set_light_style(self):
        light_palette = QPalette()
        light_palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.Button, QColor(240, 240, 240))
        light_palette.setColor(QPalette.Light, QColor(180, 180, 180))
        light_palette.setColor(QPalette.Midlight, QColor(200, 200, 200))
        light_palette.setColor(QPalette.Dark, QColor(225, 225, 225))
        light_palette.setColor(QPalette.Text, QColor(0, 0, 0))
        light_palette.setColor(QPalette.BrightText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.Base, QColor(237, 237, 237))
        light_palette.setColor(QPalette.Window, QColor(240, 240, 240))
        light_palette.setColor(QPalette.Shadow, QColor(20, 20, 20))
        light_palette.setColor(QPalette.Highlight, QColor(76, 163, 224))
        light_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.Link, QColor(0, 162, 232))
        light_palette.setColor(QPalette.AlternateBase, QColor(250, 250, 250))
        light_palette.setColor(QPalette.ToolTipBase, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.LinkVisited, QColor(222, 222, 222))
        light_palette.setColor(QPalette.Disabled, QPalette.WindowText,
                               QColor(115, 115, 115))
        light_palette.setColor(QPalette.Disabled, QPalette.Text,
                               QColor(115, 115, 115))
        light_palette.setColor(QPalette.Disabled, QPalette.ButtonText,
                               QColor(115, 115, 115))
        light_palette.setColor(QPalette.Disabled, QPalette.Highlight,
                               QColor(190, 190, 190))
        light_palette.setColor(QPalette.Disabled, QPalette.HighlightedText,
                               QColor(115, 115, 115))
        self.dialog.title_label.setStyleSheet(
            'color:white; '
            'margin-left:33px; '
            'background: none;')
        self.dialog.title_frame.setStyleSheet('''
            background: qlineargradient(
                    spread:reflect, x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgba(56, 0, 170, 255), 
                    stop:1 rgba(81, 140, 62, 255)
                )
        ''')
        self.application.setPalette(light_palette)

    def _setup_web_view_style(self) -> None:
        web_view = self.dialog.information_file_webView
        web_view.setAttribute(Qt.WA_TranslucentBackground)
        web_view.setStyleSheet("background:transparent")
        web_view.page().setBackgroundColor(Qt.transparent)

    def apply_theme(self) -> None:
        self.application.setStyle('Fusion')
        with open(os.path.join('style', 'style.qss')) as stylesheet:
            self.application.setStyleSheet(stylesheet.read())
        self._setup_web_view_style()
