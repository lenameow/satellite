import csv
import os
import time
import sys

with open('vcmcfg.csv', 'r') as csvfile:
    links = list(csv.reader(csvfile))
    print "To be downloaded: " , len(links)
    for i in range(398,len(links)):
        cmd = "wget -q " + links[i][0]
	print 'Downloading # ', i, ' ',cmd
        sys.stdout.flush()
	os.system(cmd)
	print "Downloaded #" , i
	sys.stdout.flush()
	time.sleep(22)
