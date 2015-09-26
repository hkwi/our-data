# coding: UTF-8
# kokoron.csv から「可能な限り」 geojson に変換するスクリプト。
# 不完全です。
import logging
import sys, os
import geo
import csv, codecs
import json

name2addr =dict()
name2pos = dict()
for row in csv.DictReader(codecs.open("name2address.csv", encoding="UTF-8")):
	if row["context"] != "kokoron":
		continue
	
	name2addr[row["name"]] = row["address"]
	if row["lng"] and row["lat"]:
		name2pos[row["name"]] = (row["lng"], row["lat"])

rows = []
for row in csv.DictReader(codecs.open("kokoron.csv", encoding="UTF-8")):
	name = row["name"]
	addr = name2addr.get(name)
	pos = name2pos.get(name)
	
	if addr and pos:
		pass
	else:
		results = geo.geocode(name2addr.get(name, name))
		if geo.resolved(results):
			r = results[0]
			if not pos:
				pos = (r["geometry"]["location"]["lng"], r["geometry"]["location"]["lat"])
			
			if not addr:
				addr = r["formatted_address"]
		elif results:
			for r in results:
				logging.error("{0},{1}".format(name, r["formatted_address"]))
		else:
			logging.error([name, name2addr.get(name)])
	
	if addr and pos:
		row["住所"] = addr
		rows.append({
			"type":"Feature",
			"geometry": {
				"type": "Point",
				"coordinates": pos,
			},
			"properties": row
		})

os.environ["PYTHONIOENCODING"] = "UTF-8"
json.dump({"type":"FeatureCollection","features": rows}, sys.stdout,
	indent=2, ensure_ascii=False, sort_keys=True)
