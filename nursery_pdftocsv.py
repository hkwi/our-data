import pdftableextract as pte
import glob
import csv
import os.path

def proc(input, output):
	rs = pte.table_to_list(pte.process_page(input, "1"), 1)
	w = csv.writer(open(output, "w"))
	w.writerows(rs[1])

for f in glob.glob("www.city.kobe.lg.jp/child/grow/nursery/img/*.pdf"):
	proc(f, "nursery/"+os.path.basename(f)+".csv")
