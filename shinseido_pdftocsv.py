import pdftableextract as pte
import csv
import os.path

fn = "www.city.kobe.lg.jp/child/grow/shinseido/img/20160426sisetuitiran23.pdf"
for page in range(2, 11):
	a = pte.process_page(fn, str(page))
	x = pte.table_to_list(a, page)
	with open("shinseido/%s.p%02d.csv" % (os.path.basename(fn), page), "w") as o:
		w = csv.writer(o)
		w.writerows(x[-1])
