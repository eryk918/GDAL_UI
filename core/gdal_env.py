# -*- coding: utf-8 -*-
import os

from osgeo import gdal, osr


def configure_gdal() -> None:
    data_dir = os.path.join(os.path.dirname(gdal.__file__), 'data')
    proj_dir = os.path.join(data_dir, 'proj')
    gdal_dir = os.path.join(data_dir, 'gdal')
    if os.path.isdir(proj_dir):
        osr.SetPROJSearchPaths([proj_dir])
    if os.path.isdir(gdal_dir):
        gdal.SetConfigOption('GDAL_DATA', gdal_dir)
    gdal.UseExceptions()
