# coding: UTF-8
import csv
import glob
import os.path
import sys

def remove_white(s):
	return s.replace(" ", "").replace("　", "").strip()

def proc(fn):
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
	
	body = [idx]
	for rownum, l in enumerate(data[idx_num+3:]):
		if not "".join(l):
			continue
		if "".join(l).startswith("※"):
			break
		
		body.append(l)
	
	csv.writer(sys.stdout).writerows(body)
#	print(fn, idx_idx, )

for fn in glob.glob("shinseido/*sisetuitiran1gou.pdf.p*.csv"):
	proc(fn)
