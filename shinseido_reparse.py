# coding: UTF-8
import csv
import glob
import os.path
import sys
import re
import rdflib

def remove_white(s):
	return s.replace(" ", "").replace("　", "").strip()

indent = 2

def pn_safe(s):
	PN_CHARS_BASE_re = 'A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\U00010000-\U000EFFFF'
	return re.match("^["+PN_CHARS_BASE_re+"]+$", s)

L = rdflib.Namespace("file://.#")

def proc(fn, g):
	data = [row for row in csv.reader(open(fn, encoding="UTF-8"))]
	
	# どこかから始まる 2 行は項目名に使われている
	# tuple(行番号,行) となるように探す。
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
	
	# multiindex になっていたものを flatten する
	idx = []
	idx_lv1 = set()
	prev = None
	for i in zip(idx0[1], idx1[1]):
		if i[1].startswith("終了"):
			assert not i[0]
			name = "%s %s" % (prev[0], i[1])
		elif i[0] and i[1]:
			name = "%s %s" % i
			idx_lv1.add(i[0])
		elif i[0]:
			name = i[0]
		else:
			name = i[1]
		
		idx.append(name)
		if i[0]:
			prev = i
	
	idx_idx = [n for n,x in enumerate(idx) if x and x != "所在区"] # 空を除去
	
	prev = None
	for rownum, l in enumerate(data):
		if rownum <= idx1[0]:
			continue
		
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
			assert prev, repr((n,idx[n],l))
			l[n] = prev[n]
		
		prev = l
		
		def add_field(s, v):
			m = re.match(r"^(?P<name>.*?)(（(?P<note>.*)）)?$", v)
			if m and m.group("note"):
				g.add((s, L["注"], rdflib.Literal(v)))
				v = m.group("name")
			return v
		
		def add_value(s, v, p):
			m = re.match(r"^(?P<value>.*?)\s*[\(（](?P<note>.*)[\)）]$", p)
			if v.endswith("定員") and m:
				g.add((s, L[v], rdflib.Literal(m.group("value"))))
				g.add((s, L["注"], rdflib.Literal(v+","+p)))
			elif "※" in p:
				a,b = list(map(remove_white, p.split("※", 1)))
				g.add((s, L[v], rdflib.Literal(a)))
				g.add((s, L["注"], rdflib.Literal(v+","+p)))
			else:
				g.add((s, L[v], rdflib.Literal(p)))
		
		bn = rdflib.BNode()
		for n in idx_idx:
			vs = idx[n].split()
			s = bn
			for v in vs[:-1]:
				v = add_field(s, v)
				e = list(g[s:L[v]])
				if e:
					s = e[0]
				else:
					sn = rdflib.BNode()
					g.add((s, L[v], sn))
					s = sn
			
			v = add_field(s, vs[-1])
			add_value(s, v, l[n])

g = rdflib.Graph()
g.bind("", L)
for fn in glob.glob("shinseido/*sisetuitiran23*.csv"):
	proc(fn, g)

print(g.serialize(format="turtle").decode("UTF-8"))
