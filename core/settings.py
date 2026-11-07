# -*- coding: utf-8 -*-
from PyQt6.QtCore import QSettings

ORGANIZATION = 'GDAL UI'
APPLICATION = 'GDAL UI'


def load_style() -> str:
    return str(QSettings(ORGANIZATION, APPLICATION).value('style', 'light'))


def save_style(style: str) -> None:
    QSettings(ORGANIZATION, APPLICATION).setValue('style', style)


def is_dark() -> bool:
    return load_style() == 'dark'
