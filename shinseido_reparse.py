# coding: UTF-8
import csv
import glob
import os.path
import sys

def remove_white(s):
	return s.replace(" ", "").replace("　", "").strip()

def proc(fn):
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
	body = [[idx[n] for n in idx_idx]]
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
	
	csv.writer(sys.stdout).writerows(body)
#	print(fn, idx_idx, )

for fn in glob.glob("shinseido/*sisetuitiran23.pdf.*.csv"):
	proc(fn)
