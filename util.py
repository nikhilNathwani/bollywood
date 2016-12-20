import numpy
import sys
import time
import urllib2
import csv	
import os
import json
from bs4 import BeautifulSoup

'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  web scraping  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''

def grabSiteData(url):
    usock= urllib2.urlopen(url)
    data= usock.read()
    usock.close()
    return BeautifulSoup(data,"html.parser")



'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  csv read/write  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''

def csvToLists(fn):
	rows= []
	with open(fn) as f:
		for line in f:
			arr= [elem.strip() for elem in line.split(',')]
			rows.append(arr) 
	return rows 

def listsToCSV(lists,fn):
	csv_file= open(fn,'w+')
	csv_wr = csv.writer(csv_file)
	for row in lists:
		csv_wr.writerow(row)
