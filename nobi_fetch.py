# coding: UTF-8
# のびのびパスポート施設一覧取得
import os
import re
import sys
import json
import csv
import logging
import lxml.html
import unicodedata
import zenhan
from urllib.request import urljoin, urlopen

def expect_unicode(func):
	def w(data):
		if isinstance(data, bytes):
			return func(data.decode("UTF-8")).encode("UTF-8")
		return func(data)
	return w

@expect_unicode
def normalize(data):
	NBSP = b"\xC2\xA0".decode("UTF-8")
	data = unicodedata.normalize("NFKC", zenhan.z2h(zenhan.h2z(data.replace(NBSP, ""))))
	
	# 0x2010 -- 0x2015
	dashesU8 = [b'\xe2\x80\x90', b'\xe2\x80\x91', b'\xe2\x80\x92', b'\xe2\x80\x93', b'\xe2\x80\x94', b'\xe2\x80\x95']
	dashes = "".join([s.decode("UTF-8") for s in dashesU8])
	digits = re.match("^[0-9\\+\\-{0}]+$".format(dashes), data)
	if digits:
		for d in dashes:
			data = data.replace(d, "-")
	
	return data

def fetch(location):
	(city, url) = location
	# r = lxml.html.parse(url).getroot()
	r = lxml.html.document_fromstring(urlopen(url).read().decode("CP932"))
	
	contents = r.xpath("//div[@id='contents']").pop()
	h2list = contents.xpath("./h2")
	h3list = contents.xpath("./h3")

	h2 = None
	row = None
	rows = []
	for c in contents.iterchildren():
		if c in h2list:
			h2 = c.text
		elif c in h3list:
			area_m = re.match("[１２３４５６７８９０]+．(.*?市)", h2)
			
			if h2.find("区") > 0:
				area = h2
			elif area_m:
				area = area_m.group(1)
			else:
				area = city
			
			row = dict(area=area, name=c.text)
			rows.append(row)
		
		if row is None:
			continue
		
		if c.attrib.get("class") == "link-list":
			urls = [urljoin(url, x) for x in c.xpath(".//a/@href")]
			if urls:
				row["url"] = urls[0]
				if len(urls) > 1:
					logging.error("found multiple urls {0}".format(urls))
			for x in c.xpath("./li/text()"):
				pair = x.strip().split("：", 1)
				if len(pair) > 1:
					(k,v) = map(lambda x:x.strip(), pair)
					row[k] = v
				elif "".join(pair):
					logging.error("unexpected text {0}".format(x))
	return rows

locations = [
	("神戸市", "http://www.city.kobe.lg.jp/child/education/program/nobi-kobe.html"),
	("芦屋市", "http://www.city.kobe.lg.jp/child/education/program/nobi-ashiya.html"),
	("西宮市", "http://www.city.kobe.lg.jp/child/education/program/nobi-nishinomiya.html"),
	("宝塚市", "http://www.city.kobe.lg.jp/child/education/program/nobi-takarazuka.html"),
	("三田市", "http://www.city.kobe.lg.jp/child/education/program/nobi-sanda.html"),
	("三木市", "http://www.city.kobe.lg.jp/child/education/program/nobi-miki.html"),
	("明石市", "http://www.city.kobe.lg.jp/child/education/program/nobi-akashi.html"),
	("淡路島（淡路市・洲本市・南あわじ市）・徳島市・鳴門市", "http://www.city.kobe.lg.jp/child/education/program/nobi-awajishima_naruto_tokushima.html"),
	("篠山市", "http://www.city.kobe.lg.jp/child/education/program/nobi-sasayama.html"),
	("堺市", "http://www.city.kobe.lg.jp/child/education/program/nobi-sakai.html"),
	("岸和田市", "http://www.city.kobe.lg.jp/child/education/program/nobi-kishiwada.html"),
	("紀の川市", "http://www.city.kobe.lg.jp/child/education/program/nobi-kinokawa.html"),
]

data = []
for x in map(fetch, locations):
	data += x

#print(repr(data))
#json.dump(data, sys.stdout, indent=2, ensure_ascii=False, sort_keys=True)

os.environ["PyTHONIOENCODING"] = "utf-8"
out = csv.writer(sys.stdout)
keys = set()
[keys.update(row.keys()) for row in data]
keys = sorted(keys)
out.writerow(keys)
for row in data:
	out.writerow([normalize(row.get(k,"")) for k in keys])
