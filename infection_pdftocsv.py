import pdftableextract as pte
import glob
import csv
import os.path

def proc(input, output):
	if os.path.exists(output) and os.stat(output).st_mtime > os.stat(input).st_mtime:
		return
	rs = pte.table_to_list(pte.process_page(input, "1"), 1)
	w = csv.writer(open(output, "w", encoding="UTF-8"))
	w.writerows(rs[1])

files = glob.glob("www.city.kobe.lg.jp/life/health/infection/sh*.pdf")
files += glob.glob("www.city.kobe.lg.jp/life/health/infection/trend/sh*.pdf")
files += glob.glob("www.city.kobe.lg.jp/life/health/infection/trend/*/sh*.pdf")
for f in files:
	proc(f, "infection/"+os.path.basename(f)+".csv")
