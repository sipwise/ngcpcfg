# for syntax checks
BASH_SCRIPTS =	scripts/* functions/* etc/ngcp-config/ngcpcfg.cfg helper/build_config sbin/ngcpcfg helper/tt2-wrapper
PERL_SCRIPTS =	helper/sort-yml \
		helper/sync-db \
		helper/tt2-daemon \
		helper/validate-yml helper/fileformat_version \
		sbin/ngcp-network \
		sbin/ngcp-sync-constants \
		sbin/ngcp-sync-grants
RESULTS ?= results

all: docs

docs: html pdf epub man

html:
	asciidoc docs/ngcpcfg.txt

pdf:
	a2x --icons -a toc -a toclevels=3 -a docinfo -f pdf docs/ngcpcfg.txt

epub:
	a2x --icons -a toc -a toclevels=3 -a docinfo -f epub docs/ngcpcfg.txt

man:
	asciidoc -d manpage -b docbook docs/ngcpcfg.txt
	sed -i 's/<emphasis role="strong">/<emphasis role="bold">/' docs/ngcpcfg.xml
	xsltproc --nonet /usr/share/xml/docbook/stylesheet/nwalsh/manpages/docbook.xsl docs/ngcpcfg.xml
	pod2man --section=8 sbin/ngcp-network > ngcp-network.8
	pod2man --section=8 sbin/ngcp-sync-constants > ngcp-sync-constants.8
	pod2man --section=8 sbin/ngcp-sync-grants > ngcp-sync-grants.8


clean:
	rm -f docs/ngcpcfg.xml docs/ngcpcfg.epub docs/ngcpcfg.html docs/ngcpcfg.pdf
	rm -f ngcpcfg.8 ngcp-network.8 ngcp-sync-constants.8 ngcp-sync-grants.8
	rm -rf t/__pycache__
	rm -f t/fixtures/bin/* t/*.pyc

dist-clean:
	rm -f docs/ngcpcfg.html docs/ngcpcfg.pdf
	rm -f docs/ngcpcfg.epub ngcpcfg.8

# check for syntax errors
syntaxcheck: shellcheck perlcheck

shellcheck:
	@echo -n "Checking for shell syntax errors"; \
	for SCRIPT in $(BASH_SCRIPTS); do \
		test -r $${SCRIPT} || continue ; \
		bash -n $${SCRIPT} || exit ; \
		echo -n "."; \
	done; \
	echo " done."; \

perlcheck:
	@echo "Checking for perl syntax errors:"; \
	for SCRIPT in $(PERL_SCRIPTS); do \
		test -r $${SCRIPT} || continue ; \
		perl -CSD -w -c $${SCRIPT} || exit ; \
	done; \
	echo "-> perl check done."; \

test:
	mkdir -p $(RESULTS)
	cd t ; py.test-3 --junit-xml=../$(RESULTS)/pytest.xml -v
# EOF
