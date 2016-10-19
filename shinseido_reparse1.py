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
	idx_raw = zip(*[data[idx_num+i] for i in range(3)])
	slot = []
	for idx_col in idx_raw:
		for i,v in enumerate(idx_col):
			v = remove_white(v)
			if v:
				slot = slot[:i] + [v]
		idx.append(" ".join(slot))
	
	if not out:
		return idx
	
	body = []
	for rownum, l in enumerate(data[idx_num+3:]):
		if not "".join(l):
			continue
		if "".join(l).startswith("※"):
			break
		if "".join(l).startswith("備考："):
			break
		
		body.append(l)
	
	csv.writer(out).writerows(body)
#	print(fn, idx_idx, )

for f in json.load(open("shinseido_base.json")):
	fn = f["file"]
	if not re.match(".*sisetuitiran1.*", fn):
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
