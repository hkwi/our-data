import re
import json
import glob
import csv
import jaconv
import rdflib
from rdflib.namespace import *
import csv2rdf.kouritu
import csv2rdf.itiran1
import csv2rdf.itiran23

base = None
with open("shinseido_base.json", encoding="UTF-8") as f:
	base = json.load(f)

fs = {}
for f in glob.glob("shinseido/*.pdf.p*.csv"):
	d,b,e,p = re.match("^(.*/)?(.*?)(\.p(\d+)\.csv)$", f).groups()
	k = (d,b)
	if k not in fs:
		fs[k] = []
	fs[k].append((int(p),e))

for d,b in fs.keys():
	g = rdflib.Graph()
	g.bind("dcterms", DCTERMS)
	
	info = [i for i in base if i["file"]==b][0]
	if "title" in info:
		g.add((rdflib.URIRef(""), DCTERMS["title"],
			rdflib.Literal(info["title"])))
	if "date" in info:
		g.add((rdflib.URIRef(""), DCTERMS["issued"],
			rdflib.Literal(info["date"], datatype=XSD.date)))
	
	page_idx = None
	for p,e in sorted(fs[(d,b)]):
		bulk = []
		with open(d+b+e, encoding="UTF-8") as r:
			bulk = [l for l in csv.reader(r)]
		
		def find_header_start():
			for ri, r in enumerate(bulk):
				cs = [jaconv.normalize(c).replace(" ","")
					for ci, c in enumerate(r)]
				if "施設名" in cs:
					return ri
		
		def find_header_end():
			for ri, r in enumerate(bulk):
				cs = [jaconv.normalize(c).replace(" ","")
					for ci, c in enumerate(r)]
				if "開始" in cs and "終了" in cs:
					return ri
				if "開始時間" in cs and "終了時間" in cs:
					return ri
		
		override = {}
		try:
			override = info["page"][str(p)]["fields"]
		except:
			pass
		
		def drain(idx_rows, data_rows):
			idx = []
			idx_idx = []
			slot = []
			for ci,c in enumerate(list(zip(*idx_rows))):
				if not "".join(c):
					continue
				
				for i,v in enumerate(c):
					v = jaconv.normalize(v).replace(" ","")
					if v:
						slot = slot[:i]+[v]
				
				idx.append(" ".join(slot))
				idx_idx.append(ci)
			
			data = []
			for d in data_rows:
				if not "".join([d[i] for i in idx_idx]):
					continue
				
				dr = []
				for i in idx_idx:
					dr.append(override.get(idx[len(dr)], d[i]))
				data.append(dr)
			return idx, data
		
		s = find_header_start()
		if re.search("kouritu", b):
			idx, data = drain(bulk[s:s+2], bulk[s+2:])
			assert page_idx is None or len(page_idx) == len(idx)
			csv2rdf.kouritu.capture(g, p, idx, data, info)
		elif re.search("itiran1", b):
			idx, data = drain(bulk[s:s+3], bulk[s+3:])
			assert page_idx is None or len(page_idx) == len(idx)
			csv2rdf.itiran1.capture(g, p, idx, data, info)
		elif re.search("itiran23", b):
			end = find_header_end()
			idx, data = drain(bulk[s:end+1], bulk[end+1:])
			assert page_idx is None or len(page_idx) == len(idx)
			csv2rdf.itiran23.capture(g, p, idx, data, info)
		else:
			raise ValueError(b)
		
		page_idx = idx
		
		#print(b,e,idx)
	
	with open("%s%s.ttl" % (d,b), "wb") as w:
		g.serialize(destination=w, format="turtle")
