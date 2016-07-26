# coding: UTF-8
#
# のびのびパスポート施設データ
# nobi.csv から geojson 形式のデータを生成します。
#
import logging
import sys, os
import geocoder
import csv, codecs
import json
import atexit
import pickle

GEO_FILE = "geo2.pkl"
try:
	geo = pickle.load(open(GEO_FILE, "rb"))
except:
	geo = {}

def store_geo():
	pickle.dump(geo, open(GEO_FILE, "wb"))

atexit.register(store_geo)

rows = []
fields = None
for row in csv.DictReader(codecs.open("nobi.csv", encoding="UTF-8")):
	for key in ("所在地", "name"):
		name = row[key]
		
		if name in geo:
			r = geo[name]
		else:
			r = geocoder.google(name)
			if r.ok:
				geo[name] = r
		
		if r.ok:
			rows.append({
				"type":"Feature",
				"geometry": {
					"type": "Point",
					"coordinates": [r.lng, r.lat],
				},
				"properties": row,
			})
			break
		else:
			logging.error("resolve error for {0}: {1} {2}".format(name, r.error, r.address))

os.environ["PYTHONIOENCODING"] = "UTF-8"
json.dump({"type":"FeatureCollection","features": rows}, sys.stdout,
	indent=2, ensure_ascii=False, sort_keys=True)
