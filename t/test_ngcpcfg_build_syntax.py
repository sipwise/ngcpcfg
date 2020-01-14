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
                         'OUTPUT_DIRECTORY': tmpdir,
                         'NGCPCFG': 'fixtures/ngcpcfg_carrier.cfg',
                     })

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout.replace("\\n", "\n"))
    print("stderr:")
    print(out.stderr.replace("\\n", "\n"))

    regex1 = re.compile(r"Error: Cannot process template "
                        "'.*etc/bad-syntax.txt.tt2':.*"
                        "file error - parse error - input file handle line 1: "
                        "unexpected end of directive")
    assert re.search(regex1, out.stderr)

    regex2 = re.compile(r"Error: Generating /tmp/ngcp-.*-pytest-output.*"
                        "/etc/bad-syntax.txt based on .*"
                        "/etc/bad-syntax.txt.tt2: FAILED")
    assert re.search(regex2, out.stderr)

    output_file = os.path.join(tmpdir, "etc/bad-syntax.txt")

    assert not os.path.exists(output_file)
