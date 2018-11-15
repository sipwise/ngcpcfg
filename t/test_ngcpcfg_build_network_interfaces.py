#!/usr/bin/env py.test-3

import filecmp
import os
import pytest
import re
import tempfile
import sys


@pytest.mark.tt_47255
def test_bad_syntax(ngcpcfgcli, tmpdir):
    tmpdir = tempfile.mkdtemp(prefix='ngcp-', suffix='-pytest-output')
    out = ngcpcfgcli("build", "--ignore-branch-check",
                     "/etc/network/interfaces",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'NGCP_SOCKETFILE': '/tmp/ngcpcfg.socket',
                         'OUTPUT_DIRECTORY': tmpdir,
                         'NGCPCFG': 'fixtures/ngcpcfg_network_interfaces.cfg',
                     })

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout.replace("\\n", "\n"))
    print("stderr:")
    print(out.stderr.replace("\\n", "\n"))

    regex1 = re.compile(r"Generating /etc/network/interfaces: OK")
    assert re.search(regex1, out.stdout)

    regex2 = re.compile(r"Error")
    assert not re.search(regex2, out.stdout)
    assert not re.search(regex2, out.stderr)

    output_file = os.path.join(tmpdir, "etc/network/interfaces")
    test_file = "fixtures/output/network_interfaces"
    # debug
    print("Output temp file: '%s'" % (output_temp_file))

    assert os.path.exists(output_file)
    assert os.path.exists(test_file)

    # debug
    if not filecmp.cmp(output_temp_file, test_file):
        print("output_temp_file:")
        print(open(output_temp_file).read())
        print("test_file:")
        print(open(test_file).read())
    assert filecmp.cmp(output_temp_file, test_file)
