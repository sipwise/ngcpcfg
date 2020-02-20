#!/usr/bin/env py.test-3

import filecmp
import os
import pytest
import re
import tempfile


@pytest.mark.tt_17653
def test_all_ips(ngcpcfgcli, tmpdir):
    tmpdir = tempfile.mkdtemp(prefix='ngcp-', suffix='-pytest-output')
    out = ngcpcfgcli("build", "--ignore-branch-check",
                     "/etc/kamailio/lb/db/dispatcher",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'OUTPUT_DIRECTORY': tmpdir,
                         'NGCPCFG':   'fixtures/ngcpcfg_pro.cfg',
                     })
    regex = re.compile(r"Generating " +
                       tmpdir +
                       r"/etc/kamailio/lb/db/dispatcher: OK")
    assert re.search(regex, out.stdout)
    output_file = os.path.join(tmpdir, "etc/kamailio/lb/db/dispatcher")
    test_file = "fixtures/output/dispatcher"
    assert os.path.exists(output_file)
    assert os.path.exists(test_file)
    assert filecmp.cmp(output_file, test_file)


@pytest.mark.tt_16316
def test_all_ips_carrier(ngcpcfgcli, tmpdir):
    tmpdir = tempfile.mkdtemp(prefix='ngcp-', suffix='-pytest-output')
    out = ngcpcfgcli("build", "--ignore-branch-check",
                     "/etc/kamailio/lb/db/dispatcher",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'OUTPUT_DIRECTORY': tmpdir,
                         'NGCPCFG':   'fixtures/ngcpcfg_carrier.cfg',
                     })
    regex = re.compile(r"Generating " +
                       tmpdir +
                       r"/etc/kamailio/lb/db/dispatcher: OK")
    assert re.search(regex, out.stdout)
    output_file = os.path.join(tmpdir, "etc/kamailio/lb/db/dispatcher")
    test_file = "fixtures/output/dispatcher_carrier"
    assert os.path.exists(output_file)
    assert os.path.exists(test_file)
    assert filecmp.cmp(output_file, test_file)
