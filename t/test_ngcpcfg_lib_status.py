#!/usr/bin/env py.test-3

import pytest
import re
from fixtures.fs import check_output

msg = r"Generating {}/etc/status.cfg: OK"


@pytest.mark.tt_16316
def test_status_carrier(ngcpcfgcli):
    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/status.cfg",
        env={
            "NGCPCFG": "fixtures/ngcpcfg_carrier.cfg",
        },
    )
    assert re.search(msg.format(out.env["OUTPUT_DIRECTORY"]), out.stdout)
    output_file = out.env["OUTPUT_DIRECTORY"].joinpath("etc/status.cfg")
    test_file = "fixtures/output/status.cfg_carrier"
    check_output(str(output_file), test_file)


def test_status_carrier_instances(ngcpcfgcli):
    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/status.cfg",
        env={
            "NGCPCFG": "fixtures/ngcpcfg_carrier_instances.cfg",
        },
    )
    assert re.search(msg.format(out.env["OUTPUT_DIRECTORY"]), out.stdout)
    output_file = out.env["OUTPUT_DIRECTORY"].joinpath("etc/status.cfg")
    test_file = "fixtures/output/status.cfg_carrier_instances"
    check_output(str(output_file), test_file)


def test_status_pro_instances(ngcpcfgcli):
    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/status.cfg",
        env={
            "NGCPCFG": "fixtures/ngcpcfg_pro_instances.cfg",
        },
    )
    assert re.search(msg.format(out.env["OUTPUT_DIRECTORY"]), out.stdout)
    output_file = out.env["OUTPUT_DIRECTORY"].joinpath("etc/status.cfg")
    test_file = "fixtures/output/status.cfg_pro_instances"
    check_output(str(output_file), test_file)
