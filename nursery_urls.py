import re
import lxml.html
from urllib.parse import urljoin, urlparse

base = "http://www.city.kobe.lg.jp/child/grow/shinseido/index02_03.html"
hrefs = [urljoin(base, x.get("href")) for x in lxml.html.parse(base).xpath("//a")]
pdfs = [url for url in hrefs if re.match(
	r"http://www\.city\.kobe\.lg\.jp/child/grow/nursery/img/(.*)\.pdf", url)]
for url in pdfs:
	print(url)

base = "http://www.city.kobe.lg.jp/child/grow/shinseido/index02_02.html"
hrefs = [urljoin(base, x.get("href")) for x in lxml.html.parse(base).xpath("//a")]
pdfs = [url for url in hrefs if re.match(
	r"http://www\.city\.kobe\.lg\.jp/child/grow/shinseido/img/(.*)\.pdf", url)]
for url in pdfs:
	print(url)

base = "http://www.city.kobe.lg.jp/child/grow/nursery/ninkagai/sisetu.html"
print(base)
root = lxml.html.parse(base).getroot()
root.make_links_absolute()
for href in root.xpath("//a/@href"):
	p = urlparse(href)
	if p.netloc=="www.city.kobe.lg.jp":
		for ext in (".pdf",".xls",".xlsx"):
			if p.path.lower().endswith(ext):
				print(href)
