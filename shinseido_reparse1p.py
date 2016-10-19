# coding: UTF-8
import csv
import glob
import os.path
import sys
import json
import re

def remove_white(s):
	return s.replace(" ", "").replace("　", "").strip()

def proc(fn, out):
	data = [row for row in csv.reader(open(fn, encoding="UTF-8"))]
	
	idx_num = -1
	for rownum, l in enumerate(data):
		r = [remove_white(s) for s in l]
		if "施設名" in r:
			idx_num = rownum
	
	idx = []
	idx_raw = zip(*[data[idx_num+i] for i in range(2)])
	slot = []
	for idx_col in idx_raw:
		if not "".join(idx_col):
			idx.append("")
		else:
			for i,v in enumerate(idx_col):
				v = remove_white(v)
				if v:
					slot = slot[:i] + [v]
			idx.append(" ".join(slot))
	
	ku = None
	ku_idx = idx.index("区")
	if not out:
		return idx
	
	body = []
	for rownum, l in enumerate(data[idx_num+2:]):
		if not "".join(l):
			continue # skip this line
		
		if "".join(l).startswith("※"):
			break
		
		if not l[idx.index("施設名")]:
			break
		
		if l[ku_idx]:
			ku = l[ku_idx] + "区"
		l[ku_idx] = ku
		
		body.append(l)
	
	csv.writer(out).writerows(body)
#	print(fn, idx_idx, )

for f in json.load(open("shinseido_base.json")):
	fn = f["file"]
	if not re.match(".*kourituyoutien.*", fn):
		continue
	
	idx = None
	for f in glob.glob("shinseido/%s.p*.csv" % fn):
		if idx is None:
			idx = proc(f, None)
		else:
			assert len(idx) == len(proc(f, None))
	
	fp = open("shinseido/%s.csv" % fn, "w", encoding="UTF-8")
	csv.writer(fp).writerow(idx)
	for f in glob.glob("shinseido/%s.p*.csv" % fn):
		proc(f, fp)
