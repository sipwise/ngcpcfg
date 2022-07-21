# for syntax checks
BASH_SCRIPTS = \
	scripts/* \
	functions/* \
	etc/ngcp-ngcpcfg/ngcpcfg.cfg \
	sbin/ngcpcfg
PERL_SCRIPTS = \
	lib/NGCP/Template.pm \
	helper/sort-yml \
	helper/sync-db \
	helper/tt2-process \
	helper/validate-yml helper/fileformat_version \
	sbin/ngcp-network \
	sbin/ngcp-network-validator \
	sbin/ngcp-sync-constants \
	sbin/ngcp-sync-grants \
	# EOL
YAML_SCHEMAS = \
	schemas/sites.yml \
	# EOL
RESULTS ?= results

all: docs

docs: man

man:
	asciidoctor -d manpage -b manpage docs/ngcpcfg.txt
	pod2man --section=8 sbin/ngcp-network > docs/ngcp-network.8
	pod2man --section=8 sbin/ngcp-network-validator > docs/ngcp-network-validator.8
	pod2man --section=8 sbin/ngcp-sync-constants > docs/ngcp-sync-constants.8
	pod2man --section=8 sbin/ngcp-sync-grants > docs/ngcp-sync-grants.8
	pod2man --section=3pm lib/NGCP/Template.pm > docs/NGCP::Template.3pm
	pod2man --section=3pm lib/NGCP/Template/Object.pm > docs/NGCP::Template::Object.3pm
	pod2man --section=3pm lib/NGCP/Template/Plugin/Utils.pm > docs/NGCP::Template::Plugin::Utils.3pm

clean:
	rm -f docs/*.8
	rm -f docs/*.3pm
	rm -rf t/__pycache__ t/fixtures/__pycache__/ t/*.pyc

dist-clean: clean
	rm -rf results

# check for syntax errors
syntaxcheck: shellcheck perlcheck yamlcheck

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
		perl -CSD -Ilib -w -c $${SCRIPT} || exit ; \
	done; \
	echo "-> perl check done."; \

yamlcheck:
	@echo "Checking for yaml syntax errors:"; \
	for YAML in $(YAML_SCHEMAS); do \
		test -r $${YAML} || continue ; \
		perl -MYAML::XS -E "YAML::XS::LoadFile('$${YAML}')" || exit ; \
	done; \
	echo "-> yaml check done."; \
	:

test:
	mkdir -p $(RESULTS)
	cd t ; py.test-3 --junit-xml=$(RESULTS)/pytest.xml -vv -l
# EOF
