import re
import os.path
import json
import glob
import csv
import jaconv
import rdflib
from rdflib.namespace import *
import csv2rdf.kouritu
import csv2rdf.itiran1
import csv2rdf.itiran23

fs = {}
for f in glob.glob("shinseido/*.pdf.p*.csv"):
	d,b,e,p = re.match("^(.*/)?(.*?)(\.p(\d+)\.csv)$", f).groups()
	k = (d,b)
	if k not in fs:
		fs[k] = []
	fs[k].append((int(p),e))

info = [r for r in 
	csv.DictReader(open("shinseido_meta/index.csv", encoding="UTF-8"))]

for d,b in fs.keys():
	g = rdflib.Graph()
	g.bind("dcterms", DCTERMS)
	
	csvfile = "shinseido_meta/%s" % b.replace(".pdf",".csv")
	if os.path.exists(csvfile):
		pinfo = [r for r in 
			csv.DictReader(open(csvfile, encoding="UTF-8"))]
	else:
		pinfo = []
	
	title = " ".join([p["value"] for p in pinfo if p["key"]=="title"])
	if title:
		g.add((rdflib.URIRef(""), DCTERMS["title"],
			rdflib.Literal(title)))
	
	date = "".join([p["date"] for p in info if p["file"]==b])
	if date:
		g.add((rdflib.URIRef(""), DCTERMS["issued"],
			rdflib.Literal(date, datatype=XSD.date)))
	
	page_idx = None
	for p,e in sorted(fs[(d,b)]):
		bulk = []
		try:
			with open(d+b+e, encoding="UTF-8") as r:
				bulk = [l for l in csv.reader(r)]
		except UnicodeDecodeError:
			with open(d+b+e, encoding="CP932") as r:
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
			override = {i["key"]:i["value"] for i in pinfo
				if int(i["page"])==p and not i["key"].startswith("※")}
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
			
			auto = [x in override for x in idx]
			
			def remove_dup(data_rows):
				prev = None
				data = []
				for ri,dx in enumerate(data_rows):
					if not "".join([dx[i] for i in idx_idx]):
						prev = None
						continue
					
					dr = []
					for i in idx_idx:
						dr.append(override.get(idx[len(dr)], dx[i]))
					
					if prev:
						p2 = list(prev)
						for i,r in enumerate(dr):
							if auto[i]:
								continue
							if len(prev[i])==0 and len(r)>0:
								prev[i] = r
							elif len(prev[i])>0 and len(r)==0:
								pass
							elif len(prev[i])>0 and len(r)>0:
								prev = None
								break
					
					# ct = sum([1 for x in dr if x])
					# if ct < 3:
					# 	print(ri, dr, p2)
					
					if prev is None:
						data.append(dr)
						prev = list(dr)
					else:
						# MERGE into previous line
						# print(d, b, p2, dr)
						data[-1] = prev
						prev = None
				return data
			
			return idx, remove_dup(data_rows)
		
		s = find_header_start()
		if re.search("kouritu", b):
			idx, data = drain(bulk[s:s+2], bulk[s+2:])
			assert page_idx is None or len(page_idx) == len(idx)
			csv2rdf.kouritu.capture(g, p, idx, data, pinfo)
		elif re.search("itiran(\d+nendo)?1", b):
			idx, data = drain(bulk[s:s+3], bulk[s+3:])
			assert page_idx is None or len(page_idx) == len(idx)
			csv2rdf.itiran1.capture(g, p, idx, data, pinfo)
		elif re.search("itiran23", b) or b == "291013saisyuuitiran.pdf":
			end = find_header_end()
			idx, data = drain(bulk[s:end+1], bulk[end+1:])
			assert page_idx is None or len(page_idx) == len(idx)
			csv2rdf.itiran23.capture(g, p, idx, data, pinfo)
		else:
			raise ValueError(b)
		
		page_idx = idx
		
		#print(b,e,idx)
	
	with open("%s%s.ttl" % (d,b), "wb") as w:
		g.serialize(destination=w, format="turtle")
