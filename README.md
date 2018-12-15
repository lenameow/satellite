# satellite
raster image data retrieval and regression

__Countries\_WGS84/__  
Directory containing country shape files

__Dataset4km/__  (not available)
Directory containing dataset downsample to 4km/pixel

__Dataset20km/__  
Directory containing dataset downsample to 20km/pixel

__requirement.txt__ 
Python runtime requirement

__run20km_2.db__ 
SQLite database for processing status and results

__sqlite_template.db__
SQLite database as an initial template

__pixel20km.npy__
Numpy data, pixel owned by which country.

__raster\_filename.csv__
Filenames, URLs, from NOAA

__satellite\_0\_get\_all\_file\_links.py__
Pre 0: Get links. save to raster\_filename.csv

__satellite\_1\_download\_all.py__
Pre 1: Download

__satellite\_A\_4km\_20km\_preparation.py__
Run A: Downsample utilizing gdal.warp

__satellite\_B\_countries\_4km.py__
Run B1: Calculating pixel ownership for 4km data

__satellite\_B\_countries\_20km.py__
Run B2: Calculating pixel ownership for 20km data

__satellite\_C\_process.py__
Run C: Processing (4km or 20km hard-coded)
