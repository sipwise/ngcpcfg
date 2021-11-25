#!/usr/bin/env py.test-3

import filecmp
import os
import pytest
import re

msg = r"Generating {}/etc/status.cfg: OK"


@pytest.mark.tt_16316
def test_status_carrier(ngcpcfgcli, tmpdir):
    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/status.cfg",
        env={
            "NGCPCFG": "fixtures/ngcpcfg_carrier.cfg",
        },
    )
    regex = re.compile(msg.format(out.outdir))
    assert re.search(regex, out.stdout)
    output_file = os.path.join(out.outdir, "etc/status.cfg")
    test_file = "fixtures/output/status.cfg_carrier"
    assert os.path.exists(output_file)
    assert os.path.exists(test_file)
    assert filecmp.cmp(output_file, test_file)


def test_status_carrier_instances(ngcpcfgcli, tmpdir):
    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/status.cfg",
        env={
            "NGCPCFG": "fixtures/ngcpcfg_carrier_instances.cfg",
        },
    )
    regex = re.compile(msg.format(out.outdir))
    assert re.search(regex, out.stdout)
    output_file = os.path.join(out.outdir, "etc/status.cfg")
    test_file = "fixtures/output/status.cfg_carrier_instances"
    assert os.path.exists(output_file)
    assert os.path.exists(test_file)
    assert filecmp.cmp(output_file, test_file)


def test_status_pro_instances(ngcpcfgcli, tmpdir):
    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/status.cfg",
        env={
            "NGCPCFG": "fixtures/ngcpcfg_pro_instances.cfg",
        },
    )
    regex = re.compile(msg.format(out.outdir))
    assert re.search(regex, out.stdout)
    output_file = os.path.join(out.outdir, "etc/status.cfg")
    test_file = "fixtures/output/status.cfg_pro_instances"
    assert os.path.exists(output_file)
    assert os.path.exists(test_file)
    assert filecmp.cmp(output_file, test_file)
