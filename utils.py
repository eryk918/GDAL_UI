# -*- coding: utf-8 -*-
import json
import os
import tempfile
from subprocess import run, PIPE
from typing import Optional, List, Tuple, Any, Union, Dict

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QProgressDialog, QApplication, QLayout
from osgeo import gdal

from CustomFileWidget import CustomFileWidget

APPLICATION_NAME = 'GDAL UI'
PLUGIN_DIR = os.path.normpath(os.path.dirname(__file__))
SETTINGS_PATH = os.path.join(tempfile.gettempdir(), 'gdal_ui_settings.json')

FILE_DICT_INDEXES = {
    'Data information': 0,
    'NoData value': 1,
    'Band plots': 2,
    'DEM Analysis': 2
}


def get_icon() -> QIcon:
    icon_path = os.path.join(PLUGIN_DIR, 'images', 'icon.png')
    return QIcon(icon_path)


def get_extensions(ext_type: bool = True) -> List[str]:
    """
    :type ext_type: True == raster extensions; False == vector extensions
    """
    popular_formats = [
        'img', 'png', 'jpg', 'jpeg', 'tiff', 'tif', 'gpkg', 'shp'
    ]
    raster_extensions = set()
    vector_extensions = set()
    for drv_index in range(gdal.GetDriverCount()):
        driver = gdal.GetDriver(drv_index)
        ext = driver.GetMetadataItem(gdal.DMD_EXTENSIONS)
        if ext:
            if 'DCAP_RASTER' in driver.GetMetadata_Dict():
                if len(ext.split()) > 1:
                    raster_extensions.update(set(ext.split()))
                else:
                    raster_extensions.add(ext)
            if 'DCAP_VECTOR' in driver.GetMetadata_Dict():
                if len(ext.split()) > 1:
                    vector_extensions.update(set(ext.split()))
                else:
                    vector_extensions.add(ext)
    return list(
        reversed(sorted(raster_extensions.difference(vector_extensions),
                        key=lambda extension: popular_formats.index(extension)
                        if extension in popular_formats else -1))
        if ext_type else list(reversed(sorted(
            vector_extensions.difference(raster_extensions),
            key=lambda extension: popular_formats.index(extension)
            if extension in popular_formats else -1))))


def universal_executor(cmd: str or List[str], stdout: int = PIPE,
                       shell: bool = False, input_values: Optional[str] = None,
                       encoding: str = 'utf-8', progress_bar: bool = False
                       ) -> Tuple[str, str, int, str]:
    if progress_bar:
        progress = create_progress_bar()
        progress.show()
        QApplication.processEvents()

    if isinstance(cmd, str):
        cmd = cmd.split('|')
    file = cmd[-1]

    process = run(
        cmd.split('|') if isinstance(cmd, str) else cmd, stdout=stdout,
        encoding=encoding, input=input_values, shell=shell
    )
    QApplication.processEvents()
    if progress_bar:
        progress.close()
    return process.stdout, process.stderr, process.returncode, file


def get_main_class(parent: callable) -> callable:
    while hasattr(parent, 'main_class'):
        parent = getattr(parent, 'main_class')
        if hasattr(parent, 'main_dlg'):
            return parent


def get_dialog_object(parent: callable) -> Any:
    return getattr(get_main_class(parent), 'main_dlg')


def proper_is_digit(string_num: str, ret: bool = False) -> bool or float:
    try:
        value = float(string_num.replace(',', '.'))
        return True if not ret else value
    except ValueError:
        return False


def json_to_html(
        data: Union[Dict[str, Any], List[Any]], new: bool = True,
        headers: Optional[List[str]] = None, delimiter_char: str = ':') -> str:
    color = 'rgb(0, 0, 0)'
    settings = load_settings()
    if settings.get('style') and settings['style'] == 'dark':
        color = 'rgb(190, 190, 190)'

    info = f'<table {"border=1" if new else ""} ' \
           f'style="font-family: Segoe UI, sans-serif; ' \
           f'font-size: 10pt; color:{color};">'
    if headers:
        info += f'<thead><tr><th><b>{"</b></th><td><b>".join(headers)}' \
                f'</b></th></tr></thead>'

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                info += f"<tr><th>{key}{delimiter_char}</th>" \
                        f"<td>{json_to_html(value, False)}</td></tr>"
            elif value is not None:
                info += f"<tr><th>{key}{delimiter_char}</th>" \
                        f"<td>{value}</td></tr>"
    elif isinstance(data, list):
        info += f'<ul>'
        for value in data:
            if isinstance(value, (dict, list)):
                info += f"<tr><td>{json_to_html(value, False)}</td></tr>"
            else:
                info += f"<li>{value}</li>"
        info += f"</ul>"
    info += '</table>'
    return info


def create_progress_bar(
        progress_len: int = 0, window_title: str = 'Please wait',
        window_text: str = 'Data processing is in progress..') -> QProgressDialog:
    progress = QProgressDialog()
    progress.setFixedWidth(500)
    progress.setWindowTitle(window_title)
    progress.setLabelText(window_text)
    progress.setMaximum(progress_len)
    progress.setValue(0)
    progress.setAutoClose(True)
    progress.setCancelButton(None)
    progress.setWindowIcon(get_icon())
    return progress


def safe_remove(file_path: str) -> None:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass


def load_settings() -> Dict[str, bool or str]:
    settings = {}
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r") as json_file:
                settings = json.load(json_file)
        except json.JSONDecodeError:
            pass
    return settings


def save_settings(settings_dict: Dict[str, bool or str],
                  incremental: bool = False) -> None:
    if incremental:
        tmp_settings = load_settings()
        tmp_settings.update(settings_dict)
    else:
        tmp_settings = settings_dict
    with open(SETTINGS_PATH, "w") as outfile:
        json.dump(tmp_settings, outfile)


def multiprocessing_execution(
        cmd_list: List[List[str]]) -> List[Tuple[str, str, int, str]]:
    progress = create_progress_bar()
    progress.show()
    QApplication.processEvents()

    _, temp = tempfile.mkstemp()
    with open(temp, 'w') as file:
        json.dump(cmd_list, file)
    std_out, _, _, _ = universal_executor(
        ["python", "MultiprocessingExecutor.py", temp])
    response = json.load(open(std_out.strip()))
    safe_remove(std_out.strip())
    safe_remove(temp)
    progress.close()
    return response


def insert_file_widget(destination_layout: QLayout, pos: Tuple[int, int],
                       mode: int = CustomFileWidget.GetMultipleFiles,
                       filters: str = '', default_root: str = '',
                       dialog_title: str = '',
                       action_after_use: callable = None) -> CustomFileWidget:
    if not filters:
        filters = f"({' '.join([f'*.{ext}' for ext in get_extensions()])})"
    file_widget = CustomFileWidget(
        dialog_title=dialog_title, default_root=default_root)
    file_widget._mStorageMode = mode
    file_widget.filter = filters
    if action_after_use:
        file_widget.lineEdit.textChanged.connect(action_after_use)
    destination_layout.addWidget(file_widget, *pos)
    return file_widget
