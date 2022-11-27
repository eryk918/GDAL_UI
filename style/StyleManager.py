import os

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
        darkPalette = QPalette()
        darkPalette.setColor(QPalette.WindowText, QColor(180, 180, 180))
        darkPalette.setColor(QPalette.Button, QColor(53, 53, 53))
        darkPalette.setColor(QPalette.Light, QColor(180, 180, 180))
        darkPalette.setColor(QPalette.Midlight, QColor(90, 90, 90))
        darkPalette.setColor(QPalette.Dark, QColor(35, 35, 35))
        darkPalette.setColor(QPalette.Text, QColor(180, 180, 180))
        darkPalette.setColor(QPalette.BrightText, QColor(180, 180, 180))
        darkPalette.setColor(QPalette.ButtonText, QColor(180, 180, 180))
        darkPalette.setColor(QPalette.Base, QColor(42, 42, 42))
        darkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
        darkPalette.setColor(QPalette.Shadow, QColor(20, 20, 20))
        darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        darkPalette.setColor(QPalette.HighlightedText, QColor(180, 180, 180))
        darkPalette.setColor(QPalette.Link, QColor(56, 252, 196))
        darkPalette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
        darkPalette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
        darkPalette.setColor(QPalette.ToolTipText, QColor(180, 180, 180))
        darkPalette.setColor(QPalette.LinkVisited, QColor(80, 80, 80))
        darkPalette.setColor(QPalette.Disabled, QPalette.WindowText,
                             QColor(127, 127, 127))
        darkPalette.setColor(QPalette.Disabled, QPalette.Text,
                             QColor(127, 127, 127))
        darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText,
                             QColor(127, 127, 127))
        darkPalette.setColor(QPalette.Disabled, QPalette.Highlight,
                             QColor(80, 80, 80))
        darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText,
                             QColor(127, 127, 127))
        self.application.setPalette(darkPalette)

    def set_light_style(self):
        lightPalette = QPalette()
        lightPalette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        lightPalette.setColor(QPalette.Button, QColor(240, 240, 240))
        lightPalette.setColor(QPalette.Light, QColor(180, 180, 180))
        lightPalette.setColor(QPalette.Midlight, QColor(200, 200, 200))
        lightPalette.setColor(QPalette.Dark, QColor(225, 225, 225))
        lightPalette.setColor(QPalette.Text, QColor(0, 0, 0))
        lightPalette.setColor(QPalette.BrightText, QColor(0, 0, 0))
        lightPalette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        lightPalette.setColor(QPalette.Base, QColor(237, 237, 237))
        lightPalette.setColor(QPalette.Window, QColor(240, 240, 240))
        lightPalette.setColor(QPalette.Shadow, QColor(20, 20, 20))
        lightPalette.setColor(QPalette.Highlight, QColor(76, 163, 224))
        lightPalette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        lightPalette.setColor(QPalette.Link, QColor(0, 162, 232))
        lightPalette.setColor(QPalette.AlternateBase, QColor(250, 250, 250))
        lightPalette.setColor(QPalette.ToolTipBase, QColor(240, 240, 240))
        lightPalette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        lightPalette.setColor(QPalette.LinkVisited, QColor(222, 222, 222))
        lightPalette.setColor(QPalette.Disabled, QPalette.WindowText,
                              QColor(115, 115, 115))
        lightPalette.setColor(QPalette.Disabled, QPalette.Text,
                              QColor(115, 115, 115))
        lightPalette.setColor(QPalette.Disabled, QPalette.ButtonText,
                              QColor(115, 115, 115))
        lightPalette.setColor(QPalette.Disabled, QPalette.Highlight,
                              QColor(190, 190, 190))
        lightPalette.setColor(QPalette.Disabled, QPalette.HighlightedText,
                              QColor(115, 115, 115))
        self.application.setPalette(lightPalette)

    def apply_theme(self) -> None:
        self.application.setStyle('Fusion')
        with open(os.path.join('style', 'style.qss')) as stylesheet:
            self.application.setStyleSheet(stylesheet.read())
