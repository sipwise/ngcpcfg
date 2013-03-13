all: prepare test

prepare:
	carton install

test:
	mkdir -p ../reports/
	rm -f ../reports/ngcp-network.tap
	bash ./ngcp-network > ../reports/ngcp-network.tap

clean:
	rm -rf testfiles

dist-clean: clean
	rm -rf ../reports/
	rm -rf local
