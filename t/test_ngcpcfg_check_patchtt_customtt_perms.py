#!/usr/bin/env py.test-3

import filecmp
import os
import pytest
import re
import tempfile
import sys


@pytest.mark.tt_80164
def test_ngcpcfg_check_patchtt_customtt_perms(ngcpcfgcli, tmpdir):
    path = os.getcwd()
    find = "find " + path + " -name ngcpcfg_check_patchtt_customtt_perms "
    find += "-exec ls -l {} \\;"
    out = os.popen(find).read()
    # debug, only printed in logs in case of error
    print("find out:")
    print(out)

    chmod_base = "chmod -v 0600 " + path + "/fixtures/repos/templates/etc/"
    chmod_base += "ngcpcfg_check_patchtt_customtt_perms/"

    chmod1 = chmod_base + "case-a.tt2"
    out = os.popen(chmod1).read()
    # debug, only printed in logs in case of error
    print("chmod1 out:")
    print(out)

    chmod2 = chmod_base + "case-b.customtt.tt2"
    out = os.popen(chmod2).read()
    # debug, only printed in logs in case of error
    print("chmod2 out:")
    print(out)

    out = os.popen(find).read()
    # debug, only printed in logs in case of error
    print("find out:")
    print(out)

    tmpdir = tempfile.mkdtemp(prefix='ngcp-', suffix='-pytest-output')
    out = ngcpcfgcli("check",
                     "--ignore-branch-check",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'OUTPUT_DIRECTORY': tmpdir,
                         'NGCPCFG':
                         'fixtures/ngcpcfg_check_patchtt_customtt_perms.cfg',
                         'CONFIG_POOL':
                         os.getcwd() + '/fixtures/repos/templates/etc',
                     })

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout.replace("\\n", "\n"))
    print("stderr:")
    print(out.stderr.replace("\\n", "\n"))

    regex1 = re.compile(r"Error: Permissions of customtt/patchtt file "
                        "'.*/case-a.customtt.tt2' and base file differ")
    assert re.search(regex1, out.stderr)

    regex2 = re.compile(r"Error: Permissions of customtt/patchtt file "
                        "'.*/case-b.customtt.tt2' and base file differ")
    assert re.search(regex2, out.stderr)

    regex3 = re.compile(r"Error: Base file corresponding to customtt/patchtt "
                        "file '.*/case-c.customtt.tt2' not found")
    assert re.search(regex3, out.stderr)
