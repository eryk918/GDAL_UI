# -*- coding: utf-8 -*-
import os
from subprocess import run, PIPE
from typing import Optional, List, Tuple, Any, Union, Dict

application_name = 'GDAL UI'
plugin_dir = os.path.normpath(os.path.dirname(__file__))
raster_extensions = ['tif', 'tiff', 'asc', 'img', 'xyz', 'ascii', 'png']


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
