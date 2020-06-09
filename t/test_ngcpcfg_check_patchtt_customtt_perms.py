#!/usr/bin/env py.test-3

import filecmp
import os
import pytest
import re
import tempfile
import sys


@pytest.mark.tt_80164
def test_ngcpcfg_check_patchtt_customtt_perms(ngcpcfgcli, tmpdir):
    tmpdir = tempfile.mkdtemp(prefix='ngcp-', suffix='-pytest-output')
    out = ngcpcfgcli("check",
                     "--ignore-branch-check",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'OUTPUT_DIRECTORY': tmpdir,
                         'CONFIG_POOL': './fixtures/repo/templates/etc',
                         'NGCPCFG':
                         'fixtures/ngcpcfg_check_patchtt_customtt_perms.cfg',
                     })

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout.replace("\\n", "\n"))
    print("stderr:")
    print(out.stderr.replace("\\n", "\n"))

    # regex1 = re.compile(r"Error: Cannot process template "
    #                     "'.*etc/bad-syntax.txt.tt2':.*"
    #                     "unexpected end of directive")
    # assert re.search(regex1, out.stderr)

    # regex2 = re.compile(r"Error: Generating /tmp/ngcp-.*-pytest-output.*"
    #                     "/etc/bad-syntax.txt based on .*"
    #                     "/etc/bad-syntax.txt.tt2: FAILED")
    # assert re.search(regex2, out.stderr)

    # output_file = os.path.join(tmpdir, "etc/bad-syntax.txt")

    assert not os.path.exists(output_file)
