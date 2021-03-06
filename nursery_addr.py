# coding: UTF-8
import json
import csv
import unicodedata
import geocoder
import pickle
import atexit

def trim_name(s):
	s = s.split("※")[0]
	s = s.replace("―", "ー")
	s = s.replace("（仮称）", "")
	s = s.strip().strip("　")
	s = unicodedata.normalize("NFKC", s)
	return s

shinseido = csv.DictReader(open("shinseido/all.csv", encoding="utf8"))
shinseido = list(shinseido)
status = csv.DictReader(open("nursery/all.csv", encoding="utf8"))
status = list(status)

idxtbl = [] # nersery, shinseido

for snum, row in enumerate(status):
	rname = trim_name(row["施設名"])
	addrs = [(snum, n) for n,s in enumerate(shinseido) if rname == trim_name(s["施設名"])]
	if not addrs:
		addrs = [(snum, n) for n,s in enumerate(shinseido) if rname in trim_name(s["施設名"])]
		if not addrs:
			rname = rname.split("こども園")[1].strip().strip("　")
			addrs = [(snum, n) for n,s in enumerate(shinseido) if rname in trim_name(s["施設名"])]
	
	if len(addrs) > 1:
		assert "分園" in row["施設名"]
	
	idxtbl += addrs

GEO_FILE = "geo.pkl"
try:
	geo = pickle.load(open(GEO_FILE, "rb"))
except:
	geo = {}

def store_geo():
	pickle.dump(geo, open(GEO_FILE, "wb"))

atexit.register(store_geo)

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
