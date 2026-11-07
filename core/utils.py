# -*- coding: utf-8 -*-
import html
import os
from typing import Any, Dict, List, Optional, Union

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QIcon, QDoubleValidator, QIntValidator, \
    QRegularExpressionValidator
from PyQt6.QtWidgets import QMessageBox, QWidget
from osgeo import gdal

APPLICATION_NAME = 'GDAL UI'
APP_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
POPULAR_FORMATS = ['img', 'png', 'jpg', 'jpeg', 'tiff', 'tif', 'gpkg', 'shp']


def get_icon() -> QIcon:
    return QIcon(os.path.join(APP_DIR, 'images', 'icon.png'))


def get_extensions(raster: bool = True) -> List[str]:
    raster_extensions = set()
    vector_extensions = set()
    for index in range(gdal.GetDriverCount()):
        driver = gdal.GetDriver(index)
        extensions = driver.GetMetadataItem(gdal.DMD_EXTENSIONS)
        if not extensions:
            continue
        metadata = driver.GetMetadata_Dict()
        if gdal.DCAP_RASTER in metadata:
            raster_extensions.update(extensions.split())
        if gdal.DCAP_VECTOR in metadata:
            vector_extensions.update(extensions.split())
    if raster:
        result = raster_extensions.difference(vector_extensions)
    else:
        result = vector_extensions.difference(raster_extensions)
    return sorted(
        result,
        key=lambda ext: (-POPULAR_FORMATS.index(ext)
                         if ext in POPULAR_FORMATS else 1, ext))


def file_filter(raster: bool = True, all_files: bool = True) -> str:
    patterns = ' '.join(f'*.{ext}' for ext in get_extensions(raster))
    kind = 'Rastry' if raster else 'Wektory'
    filters = [f'{kind} ({patterns})']
    if all_files:
        filters.append('Wszystkie pliki (*.*)')
    return ';;'.join(filters)


def parse_float(text: str) -> Optional[float]:
    try:
        return float(text.replace(',', '.'))
    except ValueError:
        return None


def parse_int(text: str) -> Optional[int]:
    try:
        return int(text)
    except ValueError:
        return None


def float_validator(minimum: float = -999999.9999999,
                    maximum: float = 999999.9999999,
                    precision: int = 20) -> QDoubleValidator:
    validator = QDoubleValidator(minimum, maximum, precision)
    validator.setNotation(QDoubleValidator.Notation.StandardNotation)
    return validator


def int_validator(minimum: int = -99999999,
                  maximum: int = 99999999) -> QIntValidator:
    return QIntValidator(minimum, maximum)


def regex_validator(pattern: str) -> QRegularExpressionValidator:
    return QRegularExpressionValidator(QRegularExpression(pattern))


def json_to_html(data: Union[Dict[str, Any], List[Any]],
                 headers: Optional[List[str]] = None,
                 delimiter: str = ':') -> str:
    return '<body>' + _render_node(data, True, headers, delimiter) + '</body>'


def _render_node(data: Union[Dict[str, Any], List[Any]], top: bool,
                 headers: Optional[List[str]], delimiter: str) -> str:
    border = 'border=1' if top else ''
    parts = [f'<table {border} cellpadding="3" '
             'style="font-family: Segoe UI, sans-serif; font-size: 10pt;">']
    if headers:
        cells = ''.join(f'<th><b>{html.escape(h)}</b></th>' for h in headers)
        parts.append(f'<thead><tr>{cells}</tr></thead>')
    if isinstance(data, dict):
        for key, value in data.items():
            name = html.escape(str(key))
            if isinstance(value, (dict, list)):
                parts.append(
                    f'<tr><th valign="top">{name}{delimiter}</th>'
                    f'<td>{_render_node(value, False, None, delimiter)}'
                    '</td></tr>')
            elif value is not None:
                parts.append(
                    f'<tr><th valign="top">{name}{delimiter}</th>'
                    f'<td>{html.escape(str(value))}</td></tr>')
    elif isinstance(data, list):
        for value in data:
            if isinstance(value, (dict, list)):
                parts.append(
                    f'<tr><td>{_render_node(value, False, None, delimiter)}'
                    '</td></tr>')
            else:
                parts.append(f'<tr><td>{html.escape(str(value))}</td></tr>')
    parts.append('</table>')
    return ''.join(parts)


def raster_info(path: str) -> Dict[str, Any]:
    dataset = gdal.Open(path)
    info = gdal.Info(dataset, format='json')
    bands = info.get('bands', [])
    return {
        'info': info,
        'nodata': {band['band']: band['noDataValue']
                   for band in bands if 'noDataValue' in band},
        'band_count': len(bands)
    }


def show_error(parent: QWidget, tool_name: str, text: str) -> None:
    QMessageBox.critical(parent, f'{APPLICATION_NAME} - {tool_name}', text,
                         QMessageBox.StandardButton.Ok)


def show_info(parent: QWidget, tool_name: str, text: str) -> None:
    QMessageBox.information(parent, f'{APPLICATION_NAME} - {tool_name}', text,
                            QMessageBox.StandardButton.Ok)


def ask_question(parent: QWidget, tool_name: str, text: str) -> bool:
    answer = QMessageBox.warning(
        parent, f'{APPLICATION_NAME} - {tool_name}', text,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No)
    return answer == QMessageBox.StandardButton.Yes


def error_text(error: Exception) -> str:
    return str(error).strip() or type(error).__name__
