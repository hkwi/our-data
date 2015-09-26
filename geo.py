import json, codecs, atexit, googlemaps, os

geocode_db_name = "geocode.json"
try:
	geocode_db = json.load(codecs.open(geocode_db_name, encoding="UTF-8"))
except:
	geocode_db = {}

def geocode_db_save():
	json.dump(geocode_db,
		codecs.open(geocode_db_name, "wb", encoding="UTF-8"),
		indent=2, ensure_ascii=False, sort_keys=True)

atexit.register(geocode_db_save)

gmaps = googlemaps.Client(key=os.environ["GOOGLE_API_KEY"])
def geocode(addr):
	if addr not in geocode_db:
		geocode_db[addr] = gmaps.geocode(addr)
	return geocode_db[addr]


def resolved(results):
	if not results:
		return False
	
	postal_codes = [] # useful for variants
	for r in results:
		postal = False
		for addr in r["address_components"]:
			if "postal_code" in addr["types"]:
				postal_codes.append(addr["short_name"])
				postal = True
		if not postal:
			postal_codes.append(None)
	
	politicals = [] # useful for postal code updates
	for r in results:
		political = [addr for addr in r["address_components"] if "political" in addr["types"]]
		politicals.append(json.dumps(political, sort_keys=True))
	
	if len(results) == 1 or len(set(postal_codes)) == 1 or len(set(politicals)) == 1:
		return True
	
	return False
