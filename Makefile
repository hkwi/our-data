all: nursery infection

nursery:
	python3 nursery_urls.py | wget -x -N -i -
	python nursery_pdftocsv.py

infection:
	python3 infection_urls.py | wget -x -N -i -
	python infection_pdftocsv.py
