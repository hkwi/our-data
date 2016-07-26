# coding: UTF-8
import json
import sys
import csv
import unicodedata
import geocoder
import pickle
import atexit
import re

def name_normalize(s):
	o = s
	ext = None
	s = s.split("※")[0]
	s = s.split("＊")[0]
	s = s.replace("―", "ー")
	s = s.replace("（仮称）", "")
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

data = dict()
seido = [
	("n00", "nursery/all.csv"),
	("s23", "shinseido/all23.csv"),
	("s1e", "shinseido/all1.csv"),
	("s1p", "shinseido/all1p.csv"),
	]

for s_idx,s_fname in seido:
	for d in csv.DictReader(open(s_fname, encoding="UTF-8")):
		if d["施設名"] == "施設名":
			continue
		
		key = None
		for k,v in data.items():
			if name_normalize(k)[0] == name_normalize(d["施設名"])[0]:
				key = k
				break
		
		if key is None:
			key = name_normalize(d["施設名"])[0]
			data[key] = []
		
		data[key].append((s_idx, d))

assert "夢遊喜分園" not in data

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
	
	for sendi,d in v:
		name = d["施設名"]
		_,ext = name_normalize(name)
		if ext:
			for p in places:
				if p["ext"] == ext:
					assert sendi not in p, "?"
					p[sendi] = d
		elif "分園" in name and "含む" in name:
			for p in places:
				assert sendi not in p
				p[sendi] = d
		elif len(places) == 1:
			for p in places:
				assert sendi not in p
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
	for k,_ in seido:
		if k in p:
			info.update(p[k])
	
	rows.append({
		"type":"Feature",
		"geometry": {
			"type": "Point",
			"coordinates": [ p["lng"], p["lat"] ],
		},
		"properties": info,
	})

json.dump({"type":"FeatureCollection","features": rows}, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)


sys.exit()

for idx in idxtbl:
	addr = {k:v for k,v in shinseido[idx[1]].items() if k}
	info = {k:v for k,v in status[idx[0]].items() if k}
	k = addr["所在地"]
	if k in geo:
		pass
	else:
		k2 = "神戸市 %s %s" % (info["地区"], addr["所在地"])
		g = geocoder.google(k2)
		if g.ok:
			geo[k] = g
		else:
			print(addr, info)

rows = []
for idx in idxtbl:
	addr = {k:v for k,v in shinseido[idx[1]].items() if k}
	base = {k:v for k,v in status[idx[0]].items() if k}
	a = addr["所在地"]
	
	info = {}
	for k,v in base.items():
		ks = k.split()
		if len(ks) > 1:
			if v:
				if ks[0] == "申込児童数":
					v = int(v)
					sub = "申込児童数"
				elif ks[0] == "入所の可能性":
					sub = "入所の可能性"
				else:
					raise "Unknown key name"
				
				if sub not in info:
					info[sub] = {}
				info[sub][ks[1]] = v
		else:
			info[k] = v

	rows.append({
		"type":"Feature",
		"geometry": {
			"type": "Point",
			"coordinates": [ geo[a].lng, geo[a].lat ],
		},
		"properties": info,
	})

json.dump({"type":"FeatureCollection","features": rows},
	open("nursery.json", "w"),
	indent=2, ensure_ascii=False, sort_keys=True)
