import json
import pdftableextract as pte
import csv
import os
import os.path
import glob

base = json.load(open("shinseido_base.json"))
for f in glob.glob("www.city.kobe.lg.jp/child/grow/shinseido/img/*.pdf"):
	fn = os.path.basename(f)
	out = "shinseido/%s.ttl" % fn
	if os.path.exists(out) and os.stat(out).st_mtime >= os.stat(f).st_mtime:
		continue
	
	pages = None
	for b in base:
		if b["file"] == fn:
			pages = b["pages"]
	
	assert pages, fn
	for page in range(*pages):
		a = pte.process_page(f, str(page))
		x = pte.table_to_list(a, page)
		with open("shinseido/%s.p%02d.csv" % (fn, page), "w") as o:
			w = csv.writer(o)
			w.writerows(x[-1])
