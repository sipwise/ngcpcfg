#!/usr/bin/env py.test-3

import filecmp
import os
import pytest
import re
import tempfile


@pytest.mark.tt_46601
def test_bad_syntax(ngcpcfgcli, tmpdir):
    tmpdir = tempfile.mkdtemp(prefix='ngcp-', suffix='-pytest-output')
    out = ngcpcfgcli("build", "--ignore-branch-check",
                     "/etc/bad-syntax.txt",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'NGCP_SOCKETFILE': '/tmp/ngcpcfg.socket',
                         'OUTPUT_DIRECTORY': tmpdir,
                         'NGCPCFG': 'fixtures/ngcpcfg_carrier.cfg',
                     })
    regex = re.compile(r"Generating " +
                       tmpdir +
                       r"/etc/bad-syntax.txt: OK")
    assert re.search(regex, out.stdout)
    output_file = os.path.join(tmpdir, "etc/bad-syntax.txt")
    print("Output file: '{}'", output_file)
    test_file = "fixtures/output/bad-syntax.txt"
    assert os.path.exists(output_file)
    assert os.path.exists(test_file)
    assert filecmp.cmp(output_file, test_file)
