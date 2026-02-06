#!/usr/bin/env py.test-3

import pytest
import re


@pytest.mark.tt_46601
def test_bad_syntax(ngcpcfgcli):
    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/bad-syntax.txt",
        env={
            "NGCPCFG": "fixtures/ngcpcfg_carrier.cfg",
        },
    )
    assert re.search(
        r"Error: Cannot process template " "'.*etc/bad-syntax.txt.tt2':.*",
        out.stderr,
    )
    assert re.search(
        r"file error - parse error - input file handle line 1: "
        "unexpected end of directive",
        out.stderr,
    )

    assert re.search(
        r"Error: Generating {}".format(out.env["OUTPUT_DIRECTORY"])
        + "/etc/bad-syntax.txt based on .*"
        "/etc/bad-syntax.txt.tt2: FAILED",
        out.stderr,
    )
    assert out.returncode != 0

    output_file = out.env["OUTPUT_DIRECTORY"].joinpath("etc/bad-syntax.txt")
    assert not output_file.exists()
