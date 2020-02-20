#!/usr/bin/env py.test-3

import filecmp
import os
import pytest
import re
import tempfile


@pytest.mark.tt_16316
def test_status_carrier(ngcpcfgcli, tmpdir):
    tmpdir = tempfile.mkdtemp(prefix='ngcp-', suffix='-pytest-output')
    out = ngcpcfgcli("build", "--ignore-branch-check",
                     "/etc/status.cfg",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'OUTPUT_DIRECTORY': tmpdir,
                         'NGCPCFG':   'fixtures/ngcpcfg_carrier.cfg',
                     })
    regex = re.compile(r"Generating " +
                       tmpdir +
                       r"/etc/status.cfg: OK")
    assert re.search(regex, out.stdout)
    output_file = os.path.join(tmpdir, "etc/status.cfg")
    test_file = "fixtures/output/status.cfg_carrier"
    assert os.path.exists(output_file)
    assert os.path.exists(test_file)
    assert filecmp.cmp(output_file, test_file)
