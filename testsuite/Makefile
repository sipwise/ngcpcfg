RESULTS ?= results

all: test

test:
	mkdir -p $(RESULTS)
	prove -v -I../lib . >$(RESULTS)/perl-modules.tap
	bash ./ngcp-network > $(RESULTS)/ngcp-network.tap

clean:
	rm -rf testfiles

dist-clean: clean
	rm -rf $(RESULTS)
