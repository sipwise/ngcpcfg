.PHONY: all clean demo install

all:	install demo

clean:
	rm -rf ./venv

demo:
	./venv/bin/python xls2yml network_config.xlsx > network.yml
	@echo "Wrote output to network.yml"

install:
	@echo "Installing virtual python environment"
	virtualenv -p /usr/bin/python3 ./venv
	./venv/bin/pip3 install -r requirements.txt
