import logging
import csv
import sys
import lxml.html
import feedparser
import urllib.parse

out = csv.writer(sys.stdout)
url = "http://www.city.osaka.lg.jp/shimin_top/rss/rss_705-0-0-0-0.xml"
for e in feedparser.parse(url).entries:
	if "保育施設" in e.title:
		if "空き" in e.title or "申込み" in e.title:
			out.writerow([e.link])
			root = lxml.html.parse(e.link).getroot()
			root.make_links_absolute()
			for href in root.xpath("//*[@id='mol_contents']//a/@href"):
				if urllib.parse.urlparse(href).netloc != "www.city.osaka.lg.jp":
					continue
				out.writerow([href])
				root = lxml.html.parse(href).getroot()
				root.make_links_absolute()
				for href in root.xpath("//*[@id='mol_contents']//a/@href"):
					if urllib.parse.urlparse(href).netloc != "www.city.osaka.lg.jp":
						continue
					for e in (".xls", ".xlsx", ".pdf"):
						if href.lower().endswith(e):
							out.writerow([href])
