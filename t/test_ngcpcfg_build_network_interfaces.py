#!/usr/bin/env py.test-3

import pytest
import re
from fixtures.fs import check_output


@pytest.mark.tt_47255
def test_network_interfaces(ngcpcfgcli):
    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/network/interfaces",
        env={
            "NGCPCFG": "fixtures/ngcpcfg_network_interfaces.cfg",
        },
    )

    assert re.search(r"Generating .*/etc/network/interfaces: OK", out.stdout)
    assert not re.search(r"Error", out.stdout)

    output_file = out.env["OUTPUT_DIRECTORY"].joinpath(
        "etc/network/interfaces"
    )
    test_file = "fixtures/output/network_interfaces"

    check_output(str(output_file), test_file)
