BIN=./venv/bin/
.PHONY: all clean lint run install tests

all:	install run

clean:
	rm -rf ./venv
	rm -rf network_xls2yml.egg-info __pycache__ dist build

lint:
	flake8 network_xls2yml/*.py tests/*.py
	pep8 network_xls2yml/*.py tests/*.py

run: install
	$(BIN)xls2yml input/sample_network_config_reduced.xlsx > output/generated.yml
	@echo "Wrote output to output/generated.yml"

install:
	@echo "Installing virtual python environment"
	virtualenv -p /usr/bin/python3 ./venv
	$(BIN)pip3 install -r requirements.txt
	$(BIN)python3 ./setup.py install

tests: install
	$(BIN)pytest tests/test*.py
