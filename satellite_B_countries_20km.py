import datetime
import os
import tarfile
import time
import sys

import numpy as np
import pandas as pd
import shapefile
from osgeo import gdal
from osgeo import gdalnumeric
from shapely.geometry import Point  # Point class
from shapely.geometry import shape  # shape() is a function to convert geo objects through the interface
import pickle

def pixelToEarth(pt,gt):
    pi = pt[0] + 0.5
    pj = pt[1] + 0.5
    latitude =  gt[3] + pj * gt[4] + pi * gt[5] 
    longitude = gt[0] + pj * gt[1] + pi * gt[2]
    return longitude, latitude

def findCountry(point):
    inquiringPoint = Point(point)
    for i in range(len(shape_boundary)):
        if inquiringPoint.within(shape_boundary[i]):
            return all_records[i][0]
    return 0

if __name__ == '__main__':
   
    sf = shapefile.Reader('Countries_WGS84/Countries_WGS84.shp')
    all_shapes = sf.shapes()
    all_records = sf.records()

    shape_boundary = []
    for i in range(len(all_shapes)):
        shape_boundary.append(shape(all_shapes[i]))
        
    pixelOwners20km = [];     
    
    Tile_types = ["00N060E","00N060W","00N180W","75N060E","75N060W","75N180W"]
    for k, tilename in enumerate(Tile_types):
        print("[ %d ]" % (k))
        _tif_filename = "SVDNB_npp_20180501-20180531_" + tilename + "_vcmslcfg_v10_c201806061100.avg_rade9h.tif.20km.tif"
        ds = gdal.Open("GeoFence20km/" + _tif_filename)
        width = ds.RasterXSize
        height = ds.RasterYSize
        gt = ds.GetGeoTransform()
        pixelOwner = np.zeros([height,width]);
        for i in range(height):
            print("%d%%"%(i*100/height))
            sys.stdout.flush()
            log ,lat = pixelToEarth((i,0), gt)
            if abs(lat)<=60:
                for j in range(width):
                     log,lat = pixelToEarth((i,j), gt)
                     pixelOwner[i][j] = findCountry((log,lat))
                
        pixelOwners20km.append(pixelOwner)
        del ds

    # Saving the objects:
    np.save("pixel20km.npy", pixelOwners20km)

