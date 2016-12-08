import re
import lxml.html
from urllib.parse import urljoin

base = "http://www.city.kobe.lg.jp/life/health/infection/trend/shuuhou.html"
hrefs = [urljoin(base, x.get("href")) for x in lxml.html.parse(base).xpath("//a")]
pdfs = [url for url in hrefs if re.match(
	r"http://www.city.kobe.lg.jp/life/health/infection/.*\.pdf", url)]
for url in pdfs:
	print(url)
