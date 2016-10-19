# coding: UTF-8
import csv
import glob
import json
import os.path
import sys
import re

def remove_white(s):
	return s.replace(" ", "").replace("　", "").strip()

def proc(fn, out):
	data = [row for row in csv.reader(open(fn, encoding="UTF-8"))]
	
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
	
	prev = None
	if not out:
		return [idx[n] for n in idx_idx]
	
	body = []
	for rownum, l in enumerate(data):
		if rownum > idx1[0]:
			data = [l[n] for n in idx_idx]
			if not "".join(data): # blank row
				continue
			
			# 分類は前の行を引き継ぐ
			for n in idx_idx:
				if l[n]:
					continue
				if "一時保育" in idx[n]:
					continue
				if "園庭開放" in idx[n]:
					continue
				l[n] = prev[n]
			
			prev = l
			
			body.append([l[n].split("※")[0].strip() for n in idx_idx])
	
	if out:
		csv.writer(out).writerows(body)
#	print(fn, idx_idx, )

for f in json.load(open("shinseido_base.json")):
	fn = f["file"]
	if not re.match(".*sisetuitiran23.*", fn):
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
