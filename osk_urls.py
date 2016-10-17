import csv
import sys
import lxml.html
import feedparser

out = csv.writer(sys.stdout)
url = "http://www.city.osaka.lg.jp/shimin_top/rss/rss_705-0-0-0-0.xml"
for e in feedparser.parse(url).entries:
	if "保育施設の空き" in e.title:
		out.writerow([e.link])
		root = lxml.html.parse(e.link).getroot()
		root.make_links_absolute()
		for href in root.xpath("//*[@id='mol_contents']//a/@href"):
			out.writerow([href])
			root = lxml.html.parse(href).getroot()
			root.make_links_absolute()
			for href in root.xpath("//*[@id='mol_contents']//a/@href"):
				for e in (".xls", ".xlsx", ".pdf"):
					if href.lower().endswith(e):
						out.writerow([href])
