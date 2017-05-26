#!/usr/bin/env py.test-3

import pytest


@pytest.mark.cmdline
def test_ngcpcfgcfg_ok(ngcpcfgcli):
    out = ngcpcfgcli()
    assert 'For further usage information and options ' \
           'see the ngcpcfg(8) man page' in out.stderr


@pytest.mark.cmdline
def test_ngcpcfgcfg_ko(ngcpcfgcli):
    out = ngcpcfgcli(env={'NGCPCFG': '/doesnotexist'})
    assert 'Error: Could not read configuration file ' \
           '/etc/ngcp-config/ngcpcfg.cfg. Exiting.' in out.stderr


# NOTE - this one fails if the *main* ngcpcfg.git is not
# standing on master branch, therefore use --ignore-branch-check
# until we've a mock/fixture for it
@pytest.mark.mt_16391
def test_simple_build_template_ok(ngcpcfgcli):
    out = ngcpcfgcli("build", "--ignore-branch-check",
                     "/etc/apt/apt.conf.d/71_no_recommended",
                     env={'NGCP_PORTFILE': '/tmp/ngcpcfg.port'})
    assert 'Generating /etc/apt/apt.conf.d/71_no_recommended: OK' \
        in out.stdout
