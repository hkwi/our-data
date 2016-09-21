import pdftableextract as pte
import csv
import os
import os.path
import glob

fns = glob.glob("www.city.kobe.lg.jp/child/grow/shinseido/img/*sisetuitiran23*.pdf")
fns = sorted([(os.stat(f).st_mtime, f) for f in fns], reverse=True)
fn = fns[0][1]
assert os.path.basename(fn) == "280920sisetuitiran23gou.pdf"
for page in range(2, 11):
	a = pte.process_page(fn, str(page))
	x = pte.table_to_list(a, page)
	with open("shinseido/sisetuitiran23.p%02d.csv" % page, "w") as o:
		w = csv.writer(o)
		w.writerows(x[-1])

fns = glob.glob("www.city.kobe.lg.jp/child/grow/shinseido/img/*sisetuitiran1*.pdf")
fns = sorted([(os.stat(f).st_mtime, f) for f in fns], reverse=True)
fn = fns[0][1]
assert os.path.basename(fn) == "280920sisetuitiran1gou.pdf"
for page in range(2, 6):
	a = pte.process_page(fn, str(page))
	x = pte.table_to_list(a, page)
	with open("shinseido/sisetuitiran1.p%02d.csv" % page, "w") as o:
		w = csv.writer(o)
		w.writerows(x[-1])

fns = glob.glob("www.city.kobe.lg.jp/child/grow/shinseido/img/*sisetuitirankourituyoutien.pdf")
fns = sorted([(os.stat(f).st_mtime, f) for f in fns], reverse=True)
fn = fns[0][1]
assert os.path.basename(fn) == "280920sisetuitirankourituyoutien.pdf"
a = pte.process_page(fn, "1")
x = pte.table_to_list(a, 1)
with open("shinseido/sisetuitirankourituyoutien.csv", "w") as o:
	w = csv.writer(o)
	w.writerows(x[-1])
