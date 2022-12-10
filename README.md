## GDAL UI <br> Geospatial Data Abstraction Library User Interface
**Simple graphical interface for the GDAL library**

### Description:
The application includes the implementation of the following programs:
- gdal2tiles.py
- gdalbuildvrt
- gdalcompare.py
- gdaldem
- gdalinfo
- gdalwarp
- gdal_merge.py
- gdal_translate


### Requirements:
It's recommended to use a package manager like **Conda** or **OSGeo4W**.

**Recommended python version >= 3.9.**

#### Dependencies:

```
PyQt5==5.15.7,
PyQtWebEngine>=5.15.5,
gdal>=3.4.34,
gdal2tiles,
gdal_merge,
proj,
matplotlib==3.5.1,
rasterio==1.3.3,
geopandas>=0.11.1
```

### Usage:
Clone the repository via command:

```bash
git clone https://github.com/eryk918/gdal_ui
```

Start application by:
```bash
python gdal_ui/main.py
```

