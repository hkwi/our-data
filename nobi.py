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
	for key in ("所在地", "name"):
		name = row[key]
		results = geo.geocode(name)
		if geo.resolved(results):
			r = results[0]
			rows.append({
				"type":"Feature",
				"geometry": {
					"type": "Point",
					"coordinates": [r["geometry"]["location"]["lng"], r["geometry"]["location"]["lat"]],
				},
				"properties": row,
			})
			break
		
		for r in results:
			logging.error("resolve error for {0} : {1}".format(name, r["formatted_address"]))

os.environ["PYTHONIOENCODING"] = "UTF-8"
json.dump({"type":"FeatureCollection","features": rows}, sys.stdout,
	indent=2, ensure_ascii=False, sort_keys=True)
