# coding: UTF-8
import csv
import glob

def proc(fn, out):
	w = csv.writer(open(out, "w", encoding="UTF-8"))
	idx = []
	subindex = False
	for l in csv.reader(open(fn, encoding="UTF-8")):
		if l[0] == "疾病名称":
			for i,r in reversed(list(enumerate(l))):
				if r.find("～") >= 0:
					idx = l[:i]
					break
			w.writerow(idx)
		elif l[0].find("報告定点数") >= 0:
			w.writerow([])
		elif l[0].find("定点機関から報告されたその他の感染症情報") > 0:
			break
		elif idx:
			w.writerow(l[:len(idx)])

for f in glob.glob("infection/*.pdf.csv"):
	proc(f, f.replace(".pdf", ".fmt"))
