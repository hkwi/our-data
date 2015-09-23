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

