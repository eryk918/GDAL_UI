# -*- coding: utf-8 -*-
import os

from PyQt6.QtGui import QPalette, QColor, QFontDatabase
from PyQt6.QtWidgets import QApplication, QDialog

from core.settings import load_style, save_style
from core.utils import APP_DIR

ROLE = QPalette.ColorRole
GROUP = QPalette.ColorGroup

DARK_COLORS = {
    ROLE.WindowText: (180, 180, 180),
    ROLE.Button: (53, 53, 53),
    ROLE.Light: (180, 180, 180),
    ROLE.Midlight: (90, 90, 90),
    ROLE.Dark: (35, 35, 35),
    ROLE.Text: (180, 180, 180),
    ROLE.BrightText: (180, 180, 180),
    ROLE.ButtonText: (180, 180, 180),
    ROLE.Base: (42, 42, 42),
    ROLE.Window: (53, 53, 53),
    ROLE.Shadow: (20, 20, 20),
    ROLE.Highlight: (42, 130, 218),
    ROLE.HighlightedText: (180, 180, 180),
    ROLE.Link: (56, 252, 196),
    ROLE.AlternateBase: (66, 66, 66),
    ROLE.ToolTipBase: (53, 53, 53),
    ROLE.ToolTipText: (180, 180, 180),
    ROLE.LinkVisited: (80, 80, 80),
}
DARK_DISABLED = {
    ROLE.WindowText: (127, 127, 127),
    ROLE.Text: (127, 127, 127),
    ROLE.ButtonText: (127, 127, 127),
    ROLE.Highlight: (80, 80, 80),
    ROLE.HighlightedText: (127, 127, 127),
}
LIGHT_COLORS = {
    ROLE.WindowText: (0, 0, 0),
    ROLE.Button: (240, 240, 240),
    ROLE.Light: (180, 180, 180),
    ROLE.Midlight: (200, 200, 200),
    ROLE.Dark: (225, 225, 225),
    ROLE.Text: (0, 0, 0),
    ROLE.BrightText: (0, 0, 0),
    ROLE.ButtonText: (0, 0, 0),
    ROLE.Base: (237, 237, 237),
    ROLE.Window: (240, 240, 240),
    ROLE.Shadow: (20, 20, 20),
    ROLE.Highlight: (76, 163, 224),
    ROLE.HighlightedText: (0, 0, 0),
    ROLE.Link: (0, 162, 232),
    ROLE.AlternateBase: (250, 250, 250),
    ROLE.ToolTipBase: (240, 240, 240),
    ROLE.ToolTipText: (0, 0, 0),
    ROLE.LinkVisited: (222, 222, 222),
}
LIGHT_DISABLED = {
    ROLE.WindowText: (115, 115, 115),
    ROLE.Text: (115, 115, 115),
    ROLE.ButtonText: (115, 115, 115),
    ROLE.Highlight: (190, 190, 190),
    ROLE.HighlightedText: (115, 115, 115),
}
DARK_TITLE = ('#BEBEBE', 'rgba(19, 0, 56, 255)', 'rgba(35, 61, 27, 255)')
LIGHT_TITLE = ('white', 'rgba(56, 0, 170, 255)', 'rgba(81, 140, 62, 255)')


class StyleManager:
    def __init__(self, application: QApplication, dialog: QDialog) -> None:
        self.application = application
        self.dialog = dialog
        self.application.setStyle('Fusion')
        self.application.setFont(self.dialog.font())
        QFontDatabase.addApplicationFont(
            os.path.join(APP_DIR, 'fonts', 'NotoSans-ExtraCondensedBold.ttf'))
        with open(os.path.join(APP_DIR, 'style', 'style.qss'),
                  encoding='utf-8') as stylesheet:
            self.stylesheet = stylesheet.read()

    def apply_saved_style(self) -> None:
        self.set_style(load_style())

    def set_style(self, mode: str) -> None:
        if mode == 'dark':
            self._apply_palette(DARK_COLORS, DARK_DISABLED, DARK_TITLE)
            self.dialog.settings_btn.setText('🌞')
            self.dialog.settings_btn.setChecked(True)
        else:
            mode = 'light'
            self._apply_palette(LIGHT_COLORS, LIGHT_DISABLED, LIGHT_TITLE)
            self.dialog.settings_btn.setText('🌜')
            self.dialog.settings_btn.setChecked(False)
        self.application.setStyleSheet(self.stylesheet)
        save_style(mode)

    def _apply_palette(self, colors: dict, disabled: dict,
                       title: tuple) -> None:
        palette = QPalette()
        for role, rgb in colors.items():
            palette.setColor(role, QColor(*rgb))
        for role, rgb in disabled.items():
            palette.setColor(GROUP.Disabled, role, QColor(*rgb))
        self.application.setPalette(palette)
        text_color, start, stop = title
        self.dialog.title_label.setStyleSheet(
            f'color:{text_color}; margin-left:33px; background: none;')
        self.dialog.title_frame.setStyleSheet(
            'background: qlineargradient(spread:reflect, x1:0, y1:0, '
            f'x2:1, y2:0, stop:0 {start}, stop:1 {stop})')
