import pdftableextract as pte
import glob
import csv
import os.path

def proc(input, output):
	rs = pte.table_to_list(pte.process_page(input, "1"), 1)
	w = csv.writer(open(output, "w"))
	w.writerows(rs[1])

files = glob.glob("www.city.kobe.lg.jp/life/health/infection/trend/sh*.pdf")
files += glob.glob("www.city.kobe.lg.jp/life/health/infection/trend/*/sh*.pdf")
for f in files:
	proc(f, "infection/"+os.path.basename(f)+".csv")
