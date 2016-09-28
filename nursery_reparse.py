# coding: UTF-8
import csv
import glob
import os.path

ku = dict(
	chuoku = "中央区",
	higasinadaku = "東灘区",
	hokushinhokennhukushi = "北神地区",
	hyougoku = "兵庫区",
	kitaku = "北区",
	kitasumashisyo = "北須磨",
	nadaku = "灘区",
	nagataku = "長田区",
	nishiku = "西区",
	sumaku = "須磨区",
	tarumiku = "垂水区"
)

def proc(fn, out):
	idx = []
	idx_one = []
	subindex = False
	tail = None
	ct = 0
	for l in csv.reader(open(fn)):
		if l[0] == "分類":
			idx_one = l
		elif idx_one:
			idx = []
			for a,c in zip(idx_one, l):
				a = a.replace(" ","").replace("　","")
				b = c.replace(" ","").replace("　","")
				if not b:
					if a:
						r = a
					else:
						r = ""
						prev_a = ""
				elif not a:
					if prev_a:
						r = prev_a + " " + b
					else:
						r = b
				else:
					r = a + " " + b
				idx.append(r)
				if a:
					prev_a = a
			
			if idx[-1] != "合計":
				for i,x in reversed(list(enumerate(idx))):
					if x.find("合計") >= 0:
						idx = idx[:i]+["合計"]
						tail = l[i].split("計")[1].strip().split()
						break
			
			idx_one = []
			idx = ["地区"]+idx
		elif idx:
			if not l[idx.index("組織")]:
				break
			
			if l[0]:
				cat = l[0]
			else:
				l[0] = cat
			
			l = [ku[fn.split("/")[-1].split(".")[0]]]+l
			if tail:
				if "".join(l[-6:]):
					l = l[:len(idx)-1]+[tail[ct]]
					ct += 1
				else:
					l = l[:len(idx)-1]+[""]
			
			if len(l) > len(idx):
				if "".join(l[len(idx):]):
					raise ValueError("Value index error")
				else:
					l = l[:len(idx)]
			
			if out:
				out.writerow(l)
	return idx

idx = None
for f in glob.glob("nursery/*.pdf.csv"):
	if idx is None:
		idx = proc(f, None)
	else:
		assert idx == proc(f, None), f

w = csv.writer(open("nursery/all.csv", "w"))
w.writerow(idx)
for f in glob.glob("nursery/*.pdf.csv"):
	proc(f, w)
