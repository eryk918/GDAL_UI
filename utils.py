# -*- coding: utf-8 -*-

import os
from subprocess import run, PIPE
from typing import Optional, List, Tuple, Any


plugin_dir = os.path.normpath(os.path.dirname(__file__))
raster_extensions = ['tif', 'tiff', 'asc', 'img', 'xyz', 'ascii']


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
