all: prepare test

# use our own cpan mirror
export PERL_CARTON_MIRROR=http://deb.sipwise.com/cpan/

prepare:
	carton --verbose install

test:
	mkdir -p ../reports/
	rm -f ../reports/ngcp-network.tap
	bash ./ngcp-network > ../reports/ngcp-network.tap

clean:
	rm -rf testfiles

dist-clean: clean
	rm -rf ../reports/
	rm -rf local
