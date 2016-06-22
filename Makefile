all: nursery infection nobi.json

nobi.csv:
	PYTHONIOENCODING=utf8 python3 nobi_fetch.py > nobi.csv

nobi.json:
	PYTHONIOENCODING=utf8 python3 nobi.py > nobi.json

.PHONY: nursery
nursery:
	python3 nursery_urls.py | wget -x -N -i -
	python nursery_pdftocsv.py

.PHONY: infection
infection:
	python3 infection_urls.py | wget -x -N -i -
	python infection_pdftocsv.py
