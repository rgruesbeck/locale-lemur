.PHONY: install run clean

install:
	python -m venv .venv
	.venv/bin/pip install -r requirements.txt

run: install
	.venv/bin/python translate.py

clean:
	rm -rf .venv
