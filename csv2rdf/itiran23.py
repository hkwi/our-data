import os.path
import re
import csv
import sys
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
			elif idx[i] in ("所在区","分類","受入開始月齢","卒園年齢"):
				r[i] = slot[i]
		
		obj = dict(zip(idx, r))
		R = BNode(obj["施設名"])
		
		skip = []
		for i,v in enumerate(r):
			if v == "-":
				continue
			
			k = idx[i]
			if i in skip:
				continue
			elif k in ("所在区","施設名","所在地"):
				m = re.match("(.*)(※[\d１２３４５６７８９０]*)", v)
				if m:
					v = m.group(1)
					n = notes.get(m.group(2))
					if n:
						g.add((R, NS1[k+"_備考"], Literal(n)))
					else:
						raise ValueError(v)
				if k != "所在地":
					v = jaconv.normalize(v).replace(" ","")
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
				
				m = re.match("^(?P<prefix>\d{3}-)?\d{3,4}-\d{4}$", v)
				if m:
					if m.group("prefix"):
						g.add((R, NS1["電話番号"], Literal(v)))
					else:
						g.add((R, NS1["電話番号"], Literal("078-"+v)))
				elif "予定" in v:
					g.add((R, NS1["電話番号_備考"], Literal(v)))
				elif v == "※":
					g.add((R, NS1["電話番号_備考"], Literal("相談時にお知らせいたします")))
				else:
					raise ValueError(json.dumps(v))
			elif k == "組織":
				m = re.match("^[\(（](?P<le>\w+)[\)）]$", v)
				if m: # legal entity
					g.add((R, NS1["組織"], Literal(m.group("le"))))
				else:
					print(obj, info, page)
					raise ValueError(k)
			elif k.startswith("利用定員"):
				m = re.match("^(?P<num>\d+)(?P<ext>[*＊])?(\s*[\(（](?P<loc>内地域枠\d+)[\)）])?$", v)
				if m:
					try:
						int(m.group("num"))
					except:
						raise ValueError(json.dumps(v))
					
					g.add((R, NS1["利用定員"], Literal(m.group("num"))))
					if m.group("ext"):
						g.add((R, NS1["利用定員_備考"], Literal("別途、１号認定子どもの利用定員を設けています")))
					if m.group("loc"):
						g.add((R, NS1["利用定員_備考"], Literal(m.group("loc"))))
				else:
					raise ValueError(v)
			elif k.startswith("受入開始月齢"):
				v = jaconv.normalize(v)
				m = re.match("(生後(\d+[かケヶ]月|\d+日|\d+週目)|\d+歳児|\d+歳児クラス|満\d+歳|\d+歳\d+[かケヶ]月)", v)
				if m:
					g.add((R, NS1["受入開始月齢"], Literal(v)))
				else:
					raise ValueError(json.dumps([k,v]))
			elif k == "卒園年齢":
				v = jaconv.normalize(v)
				m = re.match("※?(\d+歳[児時]クラス)", v)
				if m:
					g.add((R, NS1["卒園年齢"], Literal(m.group(1))))
				else:
					raise ValueError(v)
				
				if obj["分類"] == "家庭的保育事業":
					if v in ("0歳児クラス","※2歳児クラス"):
						g.add((R, NS1["卒園年齢_備考"], Literal("0歳の児童が入所申込み可能です")))
						g.add((R, NS1["卒園年齢_備考"], Literal("満1歳到達後は、入所申込みできません")))
						if v.startswith("※"):
							g.add((R, NS1["卒園年齢_備考"], Literal("入所中の児童は、2歳児クラスまで在籍可能です")))
					elif v in ("2歳児クラス",):
						g.add((R, NS1["卒園年齢_備考"], Literal("満3歳未満までの児童が入所申込み可能です")))
			elif re.match("^(保育(標準|短)時間|延長保育)", k):
				v = jaconv.normalize(v)
				m = re.match("(\d+:\d{2})(\s+(\d+:\d{2}))?", v)
				if m:
					name = re.match("^(保育(標準|短)時間|延長保育)", k).group(0)
					S = BNode(obj["施設名"]+name)
					g.add((R, NS1["service"], S))
					g.add((S, NS1["name"], Literal(name)))
					if m.group(3):
						v = m.group(1)
						tmend = m.group(3)
					else:
						tmend = r[i+1]
					
					if "開始" in k:
						skip.append(i+1)
						assert "終了" in idx[i+1], idx
						assert re.match("\d+:\d{2}", tmend)
						g.add((S, NS1["開始時刻"], Literal(v)))
						g.add((S, NS1["終了時刻"], Literal(r[i+1])))
					else:
						g.add((S, NS1["終了時刻"], Literal(v)))
			elif k.startswith("一時預かり"):
				v = jaconv.normalize(v)
				if v in MARU:
					S = BNode(obj["施設名"]+"一時預かり")
					g.add((R, NS1["service"], S))
					g.add((S, NS1["name"], Literal("一時預かり")))
				else:
					assert not v, json.dumps(v)
			elif k == "園庭開放":
				v = jaconv.normalize(v)
				if v in MARU:
					S = BNode(obj["施設名"]+"園庭開放")
					g.add((R, NS1["service"], S))
					g.add((S, NS1["name"], Literal("園庭開放")))
				else:
					assert not v, json.dumps(v)
			elif k.startswith("終了時間"):
				pass
			else:
				raise ValueError(k)
