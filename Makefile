.PHONY: venv build package
.DEFAULT_GOAL := clean

clean:
	rm -rf build
	rm -rf dist
	rm -f main.spec

clean-db:
	rm -f artifacts.db

clean-all: clean clean-db

venv:
	python -m venv venv

build:
	pip install pyinstaller

package:
	pyinstaller --onefile SimpleStoreNSearch.py


