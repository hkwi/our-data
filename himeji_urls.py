# coding: UTF-8
import lxml.html

r = lxml.html.parse("http://www.city.himeji.lg.jp/s50/_25179/_8980.html").getroot()
r.make_links_absolute()
for anchor in r.xpath('//*[@id="mainArea"]//a'):
	if "施設一覧" in anchor.text:
		print(anchor.get("href"))
