# coding: UTF-8
# kokoron.csv から「可能な限り」 geojson に変換するスクリプト。
# 不完全です。
import logging
import sys, os
import geo
import csv, codecs
import json

rows = []
fields = None
for row in csv.reader(codecs.open("kokoron.csv", encoding="UTF-8")):
	if fields is None:
		fields = row
		continue
	
	(name,phone) = row
	hit = False
	comps = name.split()
	while len(comps) > 0:
		results = geo.geocode(" ".join(comps))
		if len(results) > 0:
			posts = []
			for r in results:
				for addr in r["address_components"]:
					if "postal_code" in addr["types"]:
						posts.append(addr["short_name"])
			if len(results) == 1 or len(set(posts)) == 1:
				r = results[0]
				if not addr:
					addr = r["formatted_address"]
				
				rows.append({
					"type":"Feature",
					"geometry": {
						"type": "Point",
						"coordinates": [r["geometry"]["location"]["lat"], r["geometry"]["location"]["lng"]],
					},
					"properties":{
						"name": name,
						"phone": phone,
						"addr": addr,
					}
				})
			else:
				for r in results:
					logging.error("{0},{1}".format(name, r["formatted_address"]))
			hit = True
			break
		comps = comps[:-1]
	if not hit:
		logging.error(name)

os.environ["PYTHONIOENCODING"] = "UTF-8"
json.dump(rows, sys.stdout,
	indent=2, ensure_ascii=False, sort_keys=True)
