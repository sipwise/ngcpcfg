#!/usr/bin/env py.test-3

import filecmp
import os
import pytest
import re

msg = r"Generating {}/etc/kamailio/lb/db/dispatcher: OK"


@pytest.mark.tt_76851
def test_all_ips(ngcpcfgcli, tmpdir):
    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/kamailio/lb/db/dispatcher",
        env={
            "NGCPCFG": "fixtures/ngcpcfg.cfg",
        },
    )
    regex = re.compile(msg.format(out.outdir))
    assert re.search(regex, out.stdout)
    output_file = os.path.join(out.outdir, "etc/kamailio/lb/db/dispatcher")
    test_file = "fixtures/output/dispatcher"
    assert os.path.exists(output_file)
    assert os.path.exists(test_file)
    assert filecmp.cmp(output_file, test_file)


@pytest.mark.tt_17653
def test_all_ips_pro(ngcpcfgcli, tmpdir):
    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/kamailio/lb/db/dispatcher",
        env={
            "NGCPCFG": "fixtures/ngcpcfg_pro.cfg",
        },
    )
    regex = re.compile(msg.format(out.outdir))
    assert re.search(regex, out.stdout)
    output_file = os.path.join(out.outdir, "etc/kamailio/lb/db/dispatcher")
    test_file = "fixtures/output/dispatcher_pro"
    assert os.path.exists(output_file)
    assert os.path.exists(test_file)
    assert filecmp.cmp(output_file, test_file)


@pytest.mark.tt_16316
def test_all_ips_carrier(ngcpcfgcli, tmpdir):
    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/kamailio/lb/db/dispatcher",
        env={
            "NGCPCFG": "fixtures/ngcpcfg_carrier.cfg",
        },
    )
    regex = re.compile(msg.format(out.outdir))
    assert re.search(regex, out.stdout)
    output_file = os.path.join(out.outdir, "etc/kamailio/lb/db/dispatcher")
    test_file = "fixtures/output/dispatcher_carrier"
    assert os.path.exists(output_file)
    assert os.path.exists(test_file)
    assert filecmp.cmp(output_file, test_file)
