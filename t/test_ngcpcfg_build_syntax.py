#!/usr/bin/env py.test-3

import os
import pytest
import re


@pytest.mark.tt_46601
def test_bad_syntax(ngcpcfgcli, tmpdir):
    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/bad-syntax.txt",
        env={
            "NGCP_BASE_TT2": os.getcwd(),
            "NGCPCFG": "fixtures/ngcpcfg_carrier.cfg",
        },
    )

    regex1 = re.compile(
        r"Error: Cannot process template " "'.*etc/bad-syntax.txt.tt2':.*"
    )
    assert re.search(regex1, out.stderr)

    regex1 = re.compile(
        r"file error - parse error - input file handle line 1: "
        "unexpected end of directive"
    )
    assert re.search(regex1, out.stderr)

    regex2 = re.compile(
        r"Error: Generating {}".format(out.outdir) + "/etc/bad-syntax.txt based on .*"
        "/etc/bad-syntax.txt.tt2: FAILED"
    )
    assert re.search(regex2, out.stderr)

    output_file = os.path.join(tmpdir, "etc/bad-syntax.txt")

    assert not os.path.exists(output_file)
