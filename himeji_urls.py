# coding: UTF-8
import lxml.html
import html_table
import re
import jaconv
import rdflib
import urllib.parse
import os.path
import logging

DASH = "-\u2010\u2212\uff0d\u30fc"
MARU = "\u3007\u25cb"

def is_tate(s):
	if sum([1 for c in s.split("\n") if len(c)>1]):
		return False
	return True

r = lxml.html.parse("http://www.city.himeji.lg.jp/s50/_25179/_8980.html").getroot()
r.make_links_absolute()
for anchor in r.xpath('//*[@id="mainArea"]//a'):
	if "施設一覧" in anchor.text:
		href = anchor.get("href")
		print(href)
		
		g = rdflib.Graph()
		NS1 = rdflib.Namespace("http://hkwi.github.io/y0t5/terms#")
		g.bind("ns1",NS1)
		
		r = lxml.html.parse(href).getroot()
		for table in r.xpath('//*[@id="mainArea"]//table'):
			idx = None
			for row in html_table.Table(table).matrix():
				txt = [r.text_content().strip() for r in row]
				if "施設名" in txt:
					idx = row
				elif not [u.tag for u in row if u.tag=="td"]:
					idx = row
				elif idx:
					txti = lambda x:x.text_content().strip()
					
					name = None
					for k,e in zip(idx, row):
						if txti(k) == "施設名":
							name = txti(e)
					
					if name is None:
						continue
					
					b = rdflib.BNode(name)
					for i,(k,e) in enumerate(zip(idx, row)):
						ks = txti(k)
						es = txti(e)
						
						if i==0 and len(ks)==0:
							es = re.sub("\s*","", es)
							g.add((b, NS1["地区"], rdflib.Literal(es)))
						elif ks in ("バス送迎", "一時保育"):
							m = re.match("["+MARU+"]([（\(](?P<note>.*)[\)）])?", es)
							if m:
								s = rdflib.BNode(name+ks)
								g.add((b, NS1["service"], s))
								g.add((s, NS1["type"], rdflib.Literal(ks)))
								if m.group("note"):
									g.add((s, NS1["備考"],
										rdflib.Literal(m.group("note"))))
							else:
								assert not es, es
						elif ks == "電話番号":
							es = jaconv.normalize(es)
							m1 = re.match("(\d+)\-(\d+)-(\d+)", es)
							m2 = re.match("(\d+)\-(\d+)", es)
							if m1:
								p = es
							elif m2:
								p = "079-"+es
							else:
								raise ValueError(es)
							
							g.add((b, NS1[ks], rdflib.Literal(p)))
						elif ks=="施設名":
							m = re.search("(※[\d１２３４５６７８９０]*)$", es)
							if m:
								h = m.group(1)
								for si in table.xpath("following-sibling::*"):
									txt = si.text_content().strip()
									if txt.startswith(h):
										es = es[:-len(h)].strip()
										g.add((b, NS1["備考"],
											rdflib.Literal(txt[len(h):].strip())))
										break
							
							g.add((b, NS1[ks], rdflib.Literal(es)))
						elif ks in ("所在地","小学校区"):
							g.add((b, NS1[ks], rdflib.Literal(es)))
						elif ks=="設置":
							g.add((b, NS1["組織"], rdflib.Literal(es)))
						elif ks.startswith("定員") or ks.startswith("利用年齢"):
							kts = ks.split("\n")
							ets = es.split("\n")
							if kts[1:]:
								if len(ets)==1:
									ets = ets * len(kts[1:])
								else:
									assert len(ets)==len(kts[1:]), [ets, kts]
								for kt,et in zip(kts[1:],ets):
									if et in DASH:
										continue
									for i,o in enumerate("０１２３"):
										kt = kt.replace("%d号" % i, "%s号" % o)
									et = et.replace(" ","").replace("　","")
									
									s = rdflib.BNode(name+kts[0]+kt)
									g.add((b, NS1[kts[0]], s))
									g.add((s, NS1["枠"], rdflib.Literal(kt)))
									g.add((s, NS1["値"], rdflib.Literal(et)))
							else:
								es = es.replace(" ","").replace("　","")
								g.add((b, NS1[ks], rdflib.Literal(es)))
						elif "時間" in ks:
							kts = ks.split("\n")
							ets = es.split("\n")
							for kt,et in zip(kts, ets):
								if re.match("[\(（](.*)[\)）]", kt) and re.match("[\(（](.*)[\)）]", et):
									kt = kt[1:-1]
									et = et[1:-1]
								
								m = re.match("(\d+)時(\d+)分\s*～\s*(\d+)時(\d+)分", et)
								if m:
									s = rdflib.BNode(name+kt)
									g.add((b, NS1["service"], s))
									g.add((s, NS1["type"], rdflib.Literal(kt)))
									g.add((s, NS1["開始時刻"],
										rdflib.Literal(":".join(m.groups()[0:2]))))
									g.add((s, NS1["終了時刻"],
										rdflib.Literal(":".join(m.groups()[2:4]))))
								else:
									assert et in DASH, et
						else:
							raise ValueError(ks)
				else:
					logging.error(txt)
		
		ps = urllib.parse.urlparse(href)
		u = os.path.join("y0t5", ps.netloc+ps.path)
		os.makedirs(os.path.dirname(u), exist_ok=True)
		with open("%s.ttl" % u, "wb") as w:
			g.serialize(destination=w, format="turtle")
