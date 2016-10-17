import csv
import sys
import lxml.etree
import feedparser

out = csv.writer(sys.stdout)
url = "http://www.city.osaka.lg.jp/shimin_top/rss/rss_705-0-0-0-0.xml"
for e in feedparser.parse(url).entries:
	if "保育施設の空き" in e.title:
		for href in lxml.etree.parse(e.link).xpath(
				"//*[@id='mol_contents']//html:a/@href",
				namespaces=dict(html="http://www.w3.org/1999/xhtml")):
			out.writerow([href])
