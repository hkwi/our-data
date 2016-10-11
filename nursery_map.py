# coding: UTF-8
import json
import sys
import csv
import unicodedata
import geocoder
import pickle
import atexit
import re
import zenhan
import collections

name_rename = {a["旧"]:a["新"] for a
	in csv.DictReader(open("shinseido_rename.csv", encoding="UTF-8"))}

def name_normalize(s):
	def norm(s):
		s = s.split("※",1)[0]
		s = s.replace("　", " ")
		s = s.replace("－", "-")
		s = zenhan.z2h(s, mode=7)
		s = zenhan.h2z(s, mode=4)
		s = s.strip()
		return s
	s = name_rename.get(norm(s), s)
	
	o = s
	ext = None
	s = s.split("※")[0]
	s = s.split("＊")[0]
	s = s.replace("―", "ー")
	s = s.replace("（仮称）", "")
	s = s.replace("(仮称)", "")
	m = re.match("^(幼保連携型)?(認定)?(こども園)?(?P<name>.*)$", s)
	if m:
		s = m.group("name")
	
	s = s.strip().strip("　")
	
	if "分園" in s:
		m = re.match("^(?P<name>.*園)(?P<ext>　?.*?分園.*?)$", s)
		if m and m.group("name"):
			s = m.group("name")
			ext = m.group("ext").strip("　").strip()
		if s=="夢遊喜分園":
			s = "夢"
			ext = "遊喜分園"
	elif "本園" in s:
		s = s.split("本園", 1)[0]
		ext = None
	
	s = s.strip().strip("　")
	if s=="元町ちどり保育園":
		s = "神戸元町ちどり保育園"
	if s=="同朋にこにここども園":
		s = "同朋にこにこ園"
	
	s = unicodedata.normalize("NFKC", s)
	return s, ext

def location_normalize(s):
	s = s.replace("ヶ丘","が丘").replace("名谷町乙","名谷町").replace("丁目","-")
	s = s.strip().strip("　")
	s = unicodedata.normalize("NFKC", s)
	return s

data = collections.OrderedDict() # 基本名 => [(制度, 該当行), ...]
seido = [
	("状況", "nursery/all.csv"),
	("２号３号", "shinseido/all23.csv"),
	("１号", "shinseido/all1.csv"),
	("公立幼稚園", "shinseido/all1p.csv"),
	]

for s_idx,s_fname in seido:
	for d in csv.DictReader(open(s_fname, encoding="UTF-8")):
		if d["施設名"] == "施設名":
			continue
		
		key = name_normalize(d["施設名"])[0]
		if key not in data:
			data[key] = []
		
		data[key].append((s_idx, d))

assert "夢遊喜分園" not in data, "例外処理の確認"

GEO_FILE = "geo.pkl"
try:
	geo = pickle.load(open(GEO_FILE, "rb"))
except:
	geo = {}

def store_geo():
	pickle.dump(geo, open(GEO_FILE, "wb"))

atexit.register(store_geo)

for k,v in data.items():
	ls = []
	for sendi,d in v:
		l = d.get("所在地", d.get("施設所在地"))
		if l:
			ls.append(location_normalize(l))
	
	assert len(ls) > 0, repr((k,v))
	if len(ls) > 1 and len(set(ls)) != 1:
		# 分園も含む
		ldic = {}
		for sendi,d in v:
			l = d.get("所在地", d.get("施設所在地"))
			if l:
				if sendi not in ldic:
					ldic[sendi] = []
				ldic[sendi].append(l)
		
		# print(repr((k,ldic)))

# geocoder にかける前に位置情報だけを抽出する
pdata = []
for k,v in data.items():
	# 分園も含む
	places = [dict(ext=None)]
	for sendi,d in v:
		name,ext = name_normalize(d["施設名"])
		if ext and ext not in [p["ext"] for p in places]:
			places.append(dict(ext=ext))
	
	for p in places:
		p["name"] = name
	
	# これで places は dict(name=基本名, ext=分園名) の配列になる
	
	for sendi,d in v:
		name = d["施設名"]
		_,ext = name_normalize(name)
		if ext:
			for p in places:
				if p["ext"] == ext:
					assert sendi not in p, repr(["?", sendi, name, ext, p])
					p[sendi] = d
	
	for sendi,d in v:
		name = d["施設名"]
		_,ext = name_normalize(name)
		if ext:
			pass
		elif "分園" in name and "含む" in name:
			for p in places:
				if sendi not in p:
					if p["ext"] is not None:
						d2 = dict(d)
						d2["参照"] = "本園"
						p[sendi] = d2
					else:
						p[sendi] = d
		elif len(places) == 1:
			for p in places:
				assert sendi not in p, repr(["?", sendi, name])
				p[sendi] = d
		else:
			for p in places:
				if p["ext"] is None:
					assert sendi not in p
					p[sendi] = d
	
	pdata += places

for p in pdata:
	ku = set()
	ls = set()
	for k,_ in seido:
		if k in p:
			l = p[k].get("所在地", p[k].get("施設所在地"))
			if l:
				ls.add(location_normalize(l))
			
			kk = p[k].get("区", p[k].get("地区", p[k].get("所在区")))
			if kk:
				if kk == "北神地区":
					kk = "北区"
				if kk == "北須磨":
					kk = "須磨区"
				
				ku.add(kk.split("（")[0].split("(")[0])
	
	assert len(ls) == 1, repr(p)
	assert len(ku) == 1, repr(p)
	
	l = "神戸市 %s %s" % (ku.pop(), ls.pop())
	if l not in geo:
		g = geocoder.google(l)
		if g.ok:
			geo[l] = g
		else:
			raise Exception(g.error)
	
	if l in geo and not geo[l].ok:
		del(geo[l])
	
	if l in geo:
		p["lat"] = geo[l].lat
		p["lng"] = geo[l].lng

rows = []
for p in pdata:
	if "lat" not in p:
		continue
	
	if "lng" not in p:
		continue
	
	info = dict()
	for cat,_ in seido:
		if cat in p:
			for k,v in p[cat].items():
				if k:
					info["%s,%s" % (cat,k)] = v
	
	rows.append({
		"type":"Feature",
		"geometry": {
			"type": "Point",
			"coordinates": [ p["lng"], p["lat"] ],
		},
		"properties": info,
	})

json.dump({"type":"FeatureCollection","features": rows}, sys.stdout,
	ensure_ascii=False, indent=2, sort_keys=True)

