import csv
import pdftableextract as pte
import csv
import os
import os.path
import glob

for f in glob.glob("www.city.kobe.lg.jp/child/grow/shinseido/img/*.pdf"):
	fn = os.path.basename(f)
	out = "shinseido/%s.ttl" % fn
	if os.path.exists(out) and os.stat(out).st_mtime >= os.stat(f).st_mtime:
		continue
	
	info = [r for r in csv.DictReader(open("shinseido_meta/index.csv", encoding="UTF-8"))
		if r["file"] == fn]
	assert info, fn
	
	pages = [int(info[0][k]) for k in ("start","end")]
	assert pages, fn
	
	for page in range(*pages):
		a = pte.process_page(f, str(page))
		x = pte.table_to_list(a, page)
		with open("shinseido/%s.p%02d.csv" % (fn, page), "w", encoding="UTF-8") as o:
			w = csv.writer(o)
			w.writerows(x[-1])
