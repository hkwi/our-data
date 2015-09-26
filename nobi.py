# coding: UTF-8
#
# のびのびパスポート施設データ
# nobi.csv から geojson 形式のデータを生成します。
#
import logging
import sys, os
import geo
import csv, codecs
import json

rows = []
fields = None
for row in csv.DictReader(codecs.open("nobi.csv", encoding="UTF-8")):
	name = row["所在地"]
	results = geo.geocode(name)
	if geo.resolved(results):
		r = results[0]
		if not addr:
			addr = r["formatted_address"]
		
		rows.append({
			"type":"Feature",
			"geometry": {
				"type": "Point",
				"coordinates": [r["geometry"]["location"]["lng"], r["geometry"]["location"]["lat"]],
			},
			"properties": row,
		})
	elif results:
		for r in results:
			logging.error("{0},{1}".format(name, r["formatted_address"]))
	else:
		logging.error(name)

os.environ["PYTHONIOENCODING"] = "UTF-8"
json.dump({"type":"FeatureCollection","features": rows}, sys.stdout,
	indent=2, ensure_ascii=False, sort_keys=True)
