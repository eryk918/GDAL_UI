## GDAL UI: Geospatial Data Abstraction Library User Interface
**Simple graphical interface for the GDAL library**

<p align="center"><img src="https://github.com/eryk918/gdal_ui/blob/main/images/light.png?raw=true" alt="GDAL UI Light Mode" width="460"/> <img src="https://github.com/eryk918/gdal_ui/blob/main/images/dark.png?raw=true" alt="GDAL UI Dark Mode" width="460"/><p>

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

