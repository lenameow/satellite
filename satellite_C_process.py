#!/usr/bin/env python
# python2
# coding: utf-8

'''
raster processing:
unzip batch - process batch - write to database, change status - delete unzipped file

Created on Apr 30, 2018

@author: HU Chao (Lena)
'''

import datetime
import sys

import numpy as np
import pandas as pd
import shapefile
from osgeo import gdal
from osgeo import gdalnumeric
from shapely.geometry import Point  # Point class
from shapely.geometry import shape  # shape() is a function to convert geo objects through the interface

import time
from math import pi
from math import sin,cos
import sqlite3

# a = 20.833;

### downsizing rasters ###


def pixelToEarth(pt,gt):
    pi = pt[0]
    pj = pt[1]
    latitude =  gt[3] + pj * gt[4] + pi * gt[5] 
    longitude = gt[0] + pj * gt[1] + pi * gt[2]
    return longitude, latitude


def get_statistics_of_raster(ds, all_records):

    width = ds.RasterXSize
    height = ds.RasterYSize
    data = ds.GetRasterBand(1).ReadAsArray(0, 0, width, height)
    gt = ds.GetGeoTransform()

    # accumulated
    stats_accu = np.zeros(len(all_records))
    stats_area = np.zeros(len(all_records))
    R_earth = 6378.100
    A = pi * R_earth * R_earth / 180;

    for i in range(height):
        for j in range(width):
            if pixelOwner[i][j] != 0 :
                country_code = int(pixelOwner[i][j])-1
                value = data[i][j]
                log1 ,lat1 = pixelToEarth((i+0.5, j-0.5), gt)
                log2 ,lat2 = pixelToEarth((i-0.5, j+0.5), gt)
                area = A * abs((log2 - log1) * (sin(lat2*pi/180) - sin(lat1*pi/180)))
                stats_area[country_code] = stats_area[country_code] + area
                if value <= 0:
                    continue
                # if value < 0:
                #    print("value <0 (%d,%d) %f country(%d)" % (i,j,value,country_code))
                #    exit(1)
                # log1 ,lat1 = pixelToEarth((i+0.5, j-0.5), gt)
                # log2 ,lat2 = pixelToEarth((i-0.5, j+0.5), gt)
                # area = a * a * cos(lat * pi / 180.0)
                # area = A * abs((log2 - log1) * (sin(lat2*pi/180) - sin(lat1*pi/180)))
                stats_accu[country_code] = stats_accu[country_code] + value * area
                # stats_area[country_code] = stats_area[country_code] + area

    country_names = [re[1] for re in all_records]

    country_valid_bool = stats_area > 0
    country_names_valid = np.array(country_names)[country_valid_bool]
    stats_accu_valid = stats_accu[country_valid_bool]
    stats_area_valid = stats_area[country_valid_bool]

    stats = np.array([stats_accu, stats_area]).transpose()
    stats_valid = np.array([stats_accu_valid, stats_area_valid]).transpose()
    return country_names_valid, stats_valid


### save to database ###
class SQL:
    def __init__(self, *args, **kwargs):
        self.dbname = "sqlite_20km.db"

    def connect(self):
        self.conn = sqlite3.connect(self.dbname)

    def execute(self,query_name,sql):
        self.cursor = self.conn.cursor()
        self.cursor.execute(sql)
        self.conn.commit()
        self.cursor.close()

    def query(self,query_name,sql):
        self.cursor = self.conn.cursor()
        self.cursor.execute(sql)
        table_rows = self.cursor.fetchall()
        names = [description[0] for description in self.cursor.description]
        df = pd.DataFrame(table_rows, columns = names)
        # print(df.head())
        self.conn.commit()
        self.cursor.close()
        return df

    def close(self):
        self.conn.close()

    def fetchRasterFilenames(self):
        try:
            fileBatch_query_str = '''SELECT raster_file_name
                                    FROM proj_processing_status_vcmsl_0 
                                    WHERE ready_to_process = 1 AND processed_bool = 0;'''
            fileBatch = self.query('get filename batch', fileBatch_query_str)
            return fileBatch
        except sqlite3.Error as e:
            print ("Sqlite3 Error %s" % (e.args[0])) 

    def process(self,country_names_valid,stats_valid,fname):
        year_month = pd.DataFrame()
        try:
            ym_query_str = '''SELECT `year_month` FROM proj_processing_status_vcmsl_0 
                                WHERE raster_file_name = "%s";''' % fname
            year_month = self.query('get year_month', ym_query_str)

        except sqlite3.Error as e:
            print ("Sqlite3 Error :" , (e.args[0])) 
              
        int_year_month = year_month.iloc[0,0]

        for i in range(len(country_names_valid)):
            
            varlist = [country_names_valid[i], int_year_month, stats_valid[i][0], stats_valid[i][1], fname]
            insert_query_str = '''INSERT INTO proj_country_data_vcmsl_0 
                                    VALUES ("%s", %d, %f, %f, "%s");''' \
                    % (varlist[0],varlist[1],varlist[2],varlist[3],varlist[4]) # prevent duplicate
            
            try:
                self.execute('write_country_names',insert_query_str)
                
            except sqlite3.Error as e:
                print ("Sqlite3 Error :", (e.args[0])) 
                
        print ("finished writing", fname)

        # change processing status
        change_status_str = '''UPDATE proj_processing_status_vcmsl_0 SET processed_bool = 1
                                    WHERE raster_file_name = "%s";''' % fname
        try:
            self.execute('change processed_bool',change_status_str)
            print ("processed_bool changed:", fname)

        except sqlite3.Error as e:
            print ("Sqlite3 Error : ", (e.args[0]))




if __name__ == '__main__':

    ###read shapefile ###

    sf = shapefile.Reader('Countries_WGS84/Countries_WGS84.shp')
    all_records = sf.records()
    pixelOwners20km = np.load("pixel20km.npy")

    DBStats = SQL()
    DBStats.connect()
    fileBatch = DBStats.fetchRasterFilenames()
    tif_filename_lst = fileBatch['raster_file_name']
    Tile_types = ["00N060E","00N060W","00N180W","75N060E","75N060W","75N180W"]

    for _tif_filename in tif_filename_lst:
        print ("Processing file ", _tif_filename)
        sys.stdout.flush();

        for k, tile in enumerate(Tile_types):
            if tile in _tif_filename:
                pixelOwner = pixelOwners20km[k]
                break

        ### read raster file ###

        ds = gdal.Open("Dataset20kmVCMSL/"+_tif_filename)

        ### Statistics ###

        tic = datetime.datetime.now()

        country_names_valid, stats_valid = get_statistics_of_raster(ds, all_records)

        toc = datetime.datetime.now()
        print ("Statistics elapsed: " , (toc-tic))
        sys.stdout.flush();

        DBStats.process(country_names_valid, stats_valid, _tif_filename)

    DBStats.close()


