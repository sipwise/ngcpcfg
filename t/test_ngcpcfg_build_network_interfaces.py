#!/usr/bin/env py.test-3

import filecmp
import os
import pytest
import re


@pytest.mark.tt_47255
def test_network_interfaces(ngcpcfgcli, tmpdir):
    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/network/interfaces",
        env={
            "NGCP_BASE_TT2": os.getcwd(),
            "NGCPCFG": "fixtures/ngcpcfg_network_interfaces.cfg",
        },
    )

    regex1 = re.compile(r"Generating .*/etc/network/interfaces: OK")
    assert re.search(regex1, out.stdout)

    regex2 = re.compile(r"Error")
    assert not re.search(regex2, out.stdout)
    assert not re.search(regex2, out.stderr)

    output_file = os.path.join(out.outdir, "etc/network/interfaces")
    test_file = "fixtures/output/network_interfaces"

    assert os.path.exists(output_file)
    assert os.path.exists(test_file)

    # debug
    if not filecmp.cmp(output_file, test_file):
        print("output_file:")
        print(open(output_file).read())
        print("test_file:")
        print(open(test_file).read())
    assert filecmp.cmp(output_file, test_file)
