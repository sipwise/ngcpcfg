RESULTS ?= results

all: test

test:
	bash ./ngcp-network > $(RESULTS)/ngcp-network.tap

clean:
	rm -rf testfiles

dist-clean: clean
	rm -rf $(RESULTS)
