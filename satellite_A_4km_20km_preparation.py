import datetime
import os
import tarfile
import sys

from osgeo import gdal
from osgeo import gdalnumeric

import glob

if __name__ == '__main__':
    tif_avg_rade9_filename_lst = glob.glob('*.avg_rade9h.tif')
    tif_cf_cvg_filename_lst = glob.glob('*.cf_cvg.tif')

    for _tif_avg_rade9_filename in tif_avg_rade9_filename_lst:
        os.remove(_tif_avg_rade9_filename)
    for _tif_cf_cvg_filename_lst in tif_cf_cvg_filename_lst:
        os.remove(_tif_cf_cvg_filename_lst)

    tgz_filename_lst = glob.glob('Dataset_vcmslcfg/*.tgz')
    count = 0

    for _tgz_filename in tgz_filename_lst:
        print ("Processing (%d): %s" % (count,_tgz_filename))
        count = count + 1
        sys.stdout.flush()
        
        tic = datetime.datetime.now()
        tar = tarfile.open(_tgz_filename)

        # _tif_member = None
        # for member_in_tar in tar.getmembers():
        #     if 'avg_rade9h' in member_in_tar.name:
        #         _tif_member = member_in_tar
        # if _tif_member is None :
        #     print('No tif in %s' % _tgz_filename)
        #     continue
        # toc = datetime.datetime.now()        
        # print ("Fetch filename elapsed: " , (toc - tic))	
        # tic = datetime.datetime.now()

        tar.extractall() # only extract vcmsl file; ignore vcm
        tar.close()
        toc = datetime.datetime.now()
        print ("Decompression elapsed: " , (toc - tic))
        sys.stdout.flush()

        tif_avg_rade9_filename_lst = glob.glob('*.avg_rade9h.tif')
        _tif_avg_rade9_filename = tif_avg_rade9_filename_lst[0]
        tif_cf_cvg_filename_lst = glob.glob('*.cf_cvg.tif')
        _tif_cf_cvg_filename = tif_cf_cvg_filename_lst[0]

        tic = datetime.datetime.now()
        ds = gdal.Warp("Dataset4km/"+_tif_avg_rade9_filename+".4km.tif", _tif_avg_rade9_filename, dstSRS='EPSG:4326',
               outputType=gdal.GDT_Float32, xRes=0.04166666700000, yRes=0.04166666700000)
        ds = gdal.Warp("Dataset4km/"+_tif_cf_cvg_filename+".4km.tif", _tif_cf_cvg_filename, dstSRS='EPSG:4326',
               outputType=gdal.GDT_UInt16, xRes=0.04166666700000, yRes=0.04166666700000)
        ds = gdal.Warp("Dataset20km/"+_tif_avg_rade9_filename+".20km.tif", _tif_avg_rade9_filename, dstSRS='EPSG:4326',
               outputType=gdal.GDT_Float32, xRes=0.208333335, yRes=0.208333335)
        ds = gdal.Warp("Dataset20km/"+_tif_cf_cvg_filename+".20km.tif", _tif_cf_cvg_filename, dstSRS='EPSG:4326',
               outputType=gdal.GDT_UInt16, xRes=0.208333335, yRes=0.208333335)

        toc = datetime.datetime.now()
        print ("Downsampling elapsed: " , (toc - tic))
        sys.stdout.flush()

        for _tif_avg_rade9_filename in tif_avg_rade9_filename_lst:
            os.remove(_tif_avg_rade9_filename)
        for _tif_cf_cvg_filename_lst in tif_cf_cvg_filename_lst:
            os.remove(_tif_cf_cvg_filename_lst)



