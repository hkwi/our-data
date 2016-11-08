import re
import jaconv
import json
from rdflib import *
from rdflib.namespace import *

DASH = "-\u2010\u2212\uff0d\u30fc"
MARU = "\u3007\u25cb"

NS1 = Namespace("http://hkwi.github.io/y0t5/terms#")

def capture(g, page, idx, data, info):
	slot = None
	for ri, r in enumerate(data):
		line = "".join(r)
		if not line or line[0] in "※＊":
			continue
		if not "".join(r[1:]):
			continue
		
		if slot is None:
			slot = r
		
		for i,v in enumerate(r):
			if v:
				slot[i] = v
			elif idx[i] in ("区",):
				r[i] = slot[i]
		
		obj = dict(zip(idx, r))
		R = BNode(obj["施設名"])
		azukari = None
		
		skip = []
		for i, v in enumerate(r):
			k = idx[i]
			if k in ("区","施設名","施設所在地"):
				if k=="区":
					k = "所在区"
					v += "区"
				elif k=="施設所在地":
					k = "所在地"
				g.add((R, NS1[k], Literal(v)))
			elif k.startswith("募集クラス数"):
				if not v:
					continue
				
				S = BNode(obj["施設名"]+k)
				g.add((R, NS1["募集クラス"], S))
				try:
					int(v)
					g.add((S, NS1["年齢"], Literal(k.split()[1])))
					g.add((S, NS1["数"], Literal(v)))
				except:
					g.add((S, NS1["備考"], Literal(v)))
			elif k == "電話番号":
				v = jaconv.normalize(v)
				for d in DASH:
					v = v.replace(d, "-")
				
				m = re.match("^\d{3}-\d{4}$", v)
				if m:
					g.add((R, NS1["電話番号"], Literal("078-"+v)))
				elif v:
					raise ValueError(json.dumps(v))
			elif k.startswith("受入年齢"):
				if not v:
					continue
				
				assert v in MARU
				if re.search("満３～",k):
					v = "満3歳"
				elif re.search("3\s*[～ー]", k):
					v = "3歳"
				elif re.search("4\s*[～ー]", k):
					v = "4歳"
				else:
					raise ValueError(json.dumps(k))
				
				if not g.value(R, NS1["受入年齢"]):
					g.add((R, NS1["受入年齢"], Literal(v)))
			elif "預かり保育" in k:
				if v and v not in DASH:
					if "実施" in k:
						S = BNode(obj["施設名"]+"預かり保育")
						g.add((R, NS1["service"], S))
						g.add((S, NS1["name"], Literal("預かり保育")))
						g.add((S, NS1["回数"], Literal(v)))
						azukari = S
					elif "朝の" in k:
						m = re.match("(\d+:\d{2})～", v)
						if m:
							assert azukari
							g.add((azukari, NS1["朝_開始時刻"], Literal(m.group(1))))
						else:
							raise ValueError(json.dumps(v))
					elif "夕方の" in k:
						m = re.match("～(?P<tm>\d+:\d{2})([\(（](?P<note>.*?)[\)）])?", v)
						if m:
							assert azukari, obj
							g.add((azukari, NS1["夕_終了時刻"], Literal(m.group("tm"))))
							if m.group("note"):
								g.add((azukari, NS1["夕_備考"], Literal(m.group("note"))))
						else:
							for s in v.split():
								m = re.match("(\d+:\d{2})[～](\d+:\d{2})", s)
								if m:
									tm = "%s-%s" % m.groups()
									g.add((azukari, NS1["夕_終了時刻"], Literal(tm)))
								else:
									raise ValueError(json.dumps(v))
			else:
				raise ValueError(k)
