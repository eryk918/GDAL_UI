# -*- coding: utf-8 -*-
import os
from subprocess import run, PIPE
from typing import Optional, List, Tuple, Any, Union, Dict

from osgeo import gdal

application_name = 'GDAL UI'
plugin_dir = os.path.normpath(os.path.dirname(__file__))


def get_extensions(ext_type: bool = True) -> List[str]:
    """
    :type ext_type: True == raster extensions; False == vector extensions
    """

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
    return list(sorted(raster_extensions.difference(vector_extensions))) \
        if ext_type \
        else list(sorted(vector_extensions.difference(raster_extensions)))


def universal_executor(cmd: str or List[str], stdout: int = PIPE,
                       shell: bool = False, input_values: Optional[str] = None,
                       encoding: str = 'utf-8') -> Tuple[str, str, int]:
    process = run(
        cmd.split() if isinstance(cmd, str) else cmd, stdout=stdout,
        encoding=encoding, input=input_values, shell=shell
    )
    return process.stdout, process.stderr, process.returncode


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
    info = f'<table {"border=1" if new else ""} ' \
           f'style="font-family: Segoe UI, sans-serif; font-size: 10pt">'
    if headers:
        info += f'<thead><tr><th><b>{"</b></th><td><b>".join(headers)}' \
                f'</b></th></tr></thead>'

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                info += f"<tr><th>{key}{delimiter_char}</th>" \
                        f"<td>{json_to_html(value, False)}</td></tr>"
            elif value:
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
