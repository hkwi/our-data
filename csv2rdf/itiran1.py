import re
import jaconv
import json
from rdflib import *
from rdflib.namespace import *

DASH = "-\u2010\u2212\uff0d\u30fc"
MARU = "\u3007\u25cb"

NS1 = Namespace("http://hkwi.github.io/y0t5/terms#")

def capture(g, page, idx, data, info):
	try:
		notes = {p["key"]:p["value"] for p in info
			if int(p["page"])==page and p["key"].startswith("※")}
	except:
		notes = {}
	
	for r in data:
		line = "".join(r)
		if not line or line[0] in "※＊" or line.startswith("備考"):
			continue
		
		obj = dict(zip(idx, r))
		R = BNode(obj["施設名"])
		azukari = None
		
		skip = []
		for i, v in enumerate(r):
			k = idx[i]
			if k in ("所在区","施設名","所在地"):
				m = re.match("(.*)(※[１２３４５６７８９０]*)", v)
				if m:
					v = m.group(1)
					n = notes.get(m.group(2))
					if n:
						g.add((R, NS1[k+"_備考"], Literal(n)))
					else:
						raise ValueError([page, info])
				
				g.add((R, NS1[k], Literal(v)))
			elif k == "分類":
				m = re.match("^(?P<institute>.*?)([\(（](?P<finance>.*)[\)）])?$", v)
				if m:
					g.add((R, NS1["分類"], Literal(m.group("institute"))))
					if m.group("finance"):
						g.add((R, NS1["財政措置"], Literal(m.group("finance"))))
				else:
					raise ValueError(v)
			elif k == "電話番号":
				for d in DASH:
					v = v.replace(d, "-")
				
				m = re.match("^\d{3}-\d{4}$", v)
				if m:
					g.add((R, NS1["電話番号"], Literal("078-"+v)))
				elif v:
					raise ValueError(json.dumps(v))
			elif k == "組織":
				m = re.match("^[\(（](?P<le>\w+)[\)）]$", v)
				if m: # legal entity
					g.add((R, NS1["組織"], Literal(m.group("le"))))
				else:
					print(info, line, obj)
					raise ValueError(json.dumps(v))
			elif k.startswith("認可定員"):
				if v:
					try:
						int(v)
						g.add((R, NS1["認可定員"], Literal(v)))
					except:
						raise ValueError(json.dumps(v))
			elif k.startswith("受入開始年齢"):
				v = jaconv.normalize(v)
				m = re.match("\d+歳", v)
				if v:
					if not m:
						assert v in MARU, json.dumps(v)
						v = "3歳"
					
					if re.match("受入開始年齢 (歳満[～ー][3３]|満[3３]歳[～ー])", k):
						v = "満"+v
					elif re.match("受入開始年齢 ([～ー][3３]歳|[3３]歳[～ー])", k):
						pass
					else:
						raise ValueError(json.dumps(k))
					
					g.add((R, NS1["受入開始年齢"], Literal(v)))
			elif k.startswith("預かり保育"):
				v = jaconv.normalize(v)
				m = re.match("\d+:\d{2}", v)
				if m:
					S = azukari
					if azukari is None:
						azukari = S = BNode(obj["施設名"]+"預かり保育")
						g.add((R, NS1["service"], S))
						g.add((S, NS1["name"], Literal("預かり保育")))
					if re.match("預かり保育 開始時間[\(（]朝[\)）]", k):
						g.add((S, NS1["朝_開始時刻"], Literal(v)))
					elif re.match("預かり保育 終了時間[\(（]夕[\)）]", k):
						g.add((S, NS1["夕_終了時刻"], Literal(v)))
					else:
						raise ValueError(k)
				elif v in DASH:
					pass
				else:
					raise ValueError(json.dumps(v))
			elif k == "園バス":
				v = jaconv.normalize(v)
				if v in DASH:
					pass
				else:
					assert v in MARU, json.dumps(v)
					S = BNode(obj["施設名"]+"園バス")
					g.add((R, NS1["service"], S))
					g.add((S, NS1["name"], Literal("園バス")))
			elif k == "給食":
				v = jaconv.normalize(v)
				m = re.match("週\d(日|回)", v)
				if m:
					S = BNode(obj["施設名"]+"給食")
					g.add((R, NS1["service"], S))
					g.add((S, NS1["name"], Literal("給食")))
					g.add((S, NS1["回数"], Literal(v)))
				elif v in DASH:
					pass
				else:
					raise ValueError(v)
			elif k.startswith("未就園児教室"):
				v = jaconv.normalize(v)
				m = re.match("(満?\d歳|生後\d+(か|ケ)月)", v)
				if m:
					pass
				elif v == "-":
					v = None
				elif v:
					assert v in MARU, json.dumps(v)
					if re.match("未就園児教室 受入開始年齢 [１1]歳[～ー]", k):
						v = "1歳"
					elif re.match("未就園児教室 受入開始年齢 [２2]歳[～ー]", k):
						v = "2歳"
					
					assert v not in MARU, k
				
				if v:
					S = BNode(obj["施設名"]+"未就園児教室")
					g.add((R, NS1["service"], S))
					g.add((S, NS1["name"], Literal("未就園児教室")))
					g.add((S, NS1["受入開始年齢"], Literal(v)))
			elif k == "園庭開放":
				v = jaconv.normalize(v)
				if v == "-":
					pass
				elif v:
					assert v in MARU, json.dumps(v)
					S = BNode(obj["施設名"]+"園庭開放")
					g.add((R, NS1["service"], S))
					g.add((S, NS1["name"], Literal("園庭開放")))
			else:
				print(repr([k,idx]))
				raise ValueError(json.dumps(k))

