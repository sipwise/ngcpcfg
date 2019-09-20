#!/usr/bin/env py.test-3

import filecmp
import os
import pytest
import re
import tempfile
import sys


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

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout.replace("\\n", "\n"))
    print("stderr:")
    print(out.stderr.replace("\\n", "\n"))

    regex1 = re.compile(r"NOTE: Check those files for valid syntax and "
                        "encoding.*etc/bad-syntax.txt.tt2.*or inspecting "
                        "temporary /tmp/ngcpcfg.PID[0-9]+")
    assert re.search(regex1, out.stdout)

    regex2 = re.compile(r"Error: Generating /tmp/ngcp-.*-pytest-output.*"
                        "/etc/bad-syntax.txt based on .*"
                        "/etc/bad-syntax.txt.tt2: FAILED")
    assert re.search(regex2, out.stderr)

    regex3 = re.compile(r"Error:   file error - parse error - input file "
                        "handle line 1: unexpected end of directive")
    assert re.search(regex3, out.stderr)

    output_file = os.path.join(tmpdir, "etc/bad-syntax.txt")
    test_file = "fixtures/output/bad-syntax.txt"
    output_temp_file = re.sub(r".* or inspecting temporary ", "", out.stdout)
    output_temp_file = re.sub(r"\\.*", "", output_temp_file)
    # debug
    print("Output temp file: '%s'" % (output_temp_file))

    assert not os.path.exists(output_file)
    assert os.path.exists(output_temp_file)
    assert os.path.exists(test_file)

    # debug
    if not filecmp.cmp(output_temp_file, test_file):
        print("output_temp_file:")
        print(open(output_temp_file).read())
        print("test_file:")
        print(open(test_file).read())
    assert filecmp.cmp(output_temp_file, test_file)
