# coding: UTF-8
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
	if len(results) > 0:
		posts = [] # useful for variants
		for r in results:
			postal = False
			for addr in r["address_components"]:
				if "postal_code" in addr["types"]:
					posts.append(addr["short_name"])
					postal = True
			if not postal:
				posts.append(None)
		
		politicals = [] # useful for postal code updates
		for r in results:
			political = [addr for addr in r["address_components"] if "political" in addr["types"]]
			politicals.append(json.dumps(political, sort_keys=True))
		
		if len(results) == 1 or len(set(posts)) == 1 or len(set(politicals)) == 1:
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
		else:
			for r in results:
				logging.error("{0},{1}".format(name, r["formatted_address"]))
	else:
		logging.error(name)

os.environ["PYTHONIOENCODING"] = "UTF-8"
json.dump({"type":"FeatureCollection","features": rows}, sys.stdout,
	indent=2, ensure_ascii=False, sort_keys=True)
