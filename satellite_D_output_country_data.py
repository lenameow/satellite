import numpy as np
import pandas as pd

import sqlite3

import shapefile
from shapely.geometry import Point  # Point class
from shapely.geometry import shape  # shape() is a function to convert geo objects through the interface


class SQL:
    def __init__(self, *args, **kwargs):
        self.dbname = "sqlite_20km.db"

    def connect(self):
        self.conn = sqlite3.connect(self.dbname)

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


if __name__ == '__main__':

    ###read shapefile ###

    sf = shapefile.Reader('Countries_WGS84/Countries_WGS84.shp')
    all_records = sf.records()
    country_names = [re[1] for re in all_records]
    # print(country_names)

    DBStats = SQL()
    DBStats.connect()

    for country_name in country_names:
        
        try:
            country_data = DBStats.query("get country data:", '''SELECT country_name, year_month, sum(lumi), sum(area) \
            FROM proj_country_data_vcmsl_0 \
            WHERE country_name = '%s' \
            GROUP BY year_month;''' % country_name)

            country_data.to_csv('country-lumi-data/%s.csv' % country_name)

        except Exception, e:
            print(country_name, e)

    DBStats.close()
