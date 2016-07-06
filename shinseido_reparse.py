# coding: UTF-8
import csv
import glob
import os.path
import sys

def remove_white(s):
	return s.replace(" ", "").replace("　", "").strip()

def proc(fn):
	data = []
	for row in csv.reader(open(fn, encoding="UTF-8")):
		row = [remove_white(s) for s in row]
		if "".join(row):
			data.append(row)
	
	idx0 = (-1, None)
	idx1 = (-1, None)
	
	for rownum, l in enumerate(data):
		r = [remove_white(s) for s in l]
		if "施設名" in r:
			idx0 = (rownum, r)
		if "開始" in r and "終了" in r:
			idx1 = (rownum, r)
		if "開始時間" in r and "終了時間" in r:
			idx1 = (rownum, r)
	
	idx = [" ".join(l).strip() for l in zip(idx0[1], idx1[1])]
	idx_idx = [n for n,x in enumerate(idx) if x and x != "所在区"]
	
	bunrui = None
	bunrui_idx = idx.index("分類")
	body = [[idx[n] for n in idx_idx]]
	for rownum, l in enumerate(data):
		if rownum > idx1[0]:
			if not l[idx.index("施設名")]:
				break
			
			if l[bunrui_idx]:
				bunrui = l[bunrui_idx]
			else:
				l[bunrui_idx] = bunrui
			
			body.append([l[n] for n in idx_idx])
	
	csv.writer(sys.stdout).writerows(body)
#	print(fn, idx_idx, )

for fn in glob.glob("shinseido/*.pdf.*.csv"):
	proc(fn)
