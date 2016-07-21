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
	body = [idx]
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
	
	csv.writer(sys.stdout).writerows(body)
#	print(fn, idx_idx, )

for fn in glob.glob("shinseido/*kourituyoutien.pdf.csv"):
	proc(fn)
