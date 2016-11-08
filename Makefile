all: nursery infection nobi.json osk carenet repo

nobi:
	PYTHONIOENCODING=utf8 python3 nobi_fetch.py > nobi.csv

nobi.json: nobi
	PYTHONIOENCODING=utf8 python3 nobi.py > nobi.json

.PHONY: nursery
nursery:
	python3 nursery_urls.py | wget -x -N -i -
	python nursery_pdftocsv.py
	python3 nursery_reparse.py
	python shinseido_pdftocsv.py
	python3 shinseido_reparse.py
	#PYTHONIOENCODING=utf8 python3 nursery_map.py > shinseido.json

.PHONY: carenet
carenet:
	wget -N -np -r http://www.city.kobe.lg.jp/life/support/carenet/shisetsu/index.html

.PHONY: infection
infection:
	python3 infection_urls.py | wget -x -N -i -
	python infection_pdftocsv.py
	python3 infection_reparse.py

osk:
	python3 osk_urls.py | wget -x -N -i -

.PHONY: repo
	git add infection
	git add www.city.kobe.lg.jp
