from bs4 import BeautifulSoup
import urllib2
import re
import pandas as pd
import csv


html_page = urllib2.urlopen("https://www.ngdc.noaa.gov/eog/viirs/download_dnb_composites_iframe.html")
soup = BeautifulSoup(html_page)

links = []

for link in soup.find_all(href = re.compile("vcmslcfg")):
    print (link.get('href'))
    links.append(link.get('href'))
print(len(links))

result_file = open("vcmcslfg.csv",'w')
wr = csv.writer(result_file, dialect='excel')
for item in links:
    wr.writerow([item,])