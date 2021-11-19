#!/usr/bin/env py.test-3

from pathlib import Path
import pytest
import re
from fixtures.fs import check_output, check_stdoutput


def test_build_instances(ngcpcfgcli):
    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/kamailio",
        env={
            "NGCP_HOSTNAME": "lb01a",
            "TEMPLATE_POOL_BASE": "fixtures/build_instances",
            "TEMPLATE_INSTANCES": "fixtures/repos/ngcp.instances",
            "NGCPCFG": "fixtures/ngcpcfg_carrier_instances.cfg",
        },
    )
    assert re.search(r"Generating .*/etc/kamailio/lb/kamailio.cfg: OK", out.stdout)

    assert not re.search(r"Error", out.stdout)
    assert not re.search(r"Error", out.stderr)

    base_dir = out.env["OUTPUT_DIRECTORY"]
    output_file = base_dir.joinpath("etc/kamailio/lb/kamailio.cfg")
    test_file = "fixtures/output/lb_kamailio_cfg_carrier"

    check_output(str(output_file), test_file)

    assert re.search(r"Generating .*/etc/kamailio/lb_A/kamailio.cfg: OK", out.stdout)

    output_file = base_dir.joinpath("etc/kamailio/lb_A/kamailio.cfg")
    test_file = "fixtures/output/lb_kamailio_cfg_instances_A"

    check_output(str(output_file), test_file)

    assert re.search(r"Generating .*/etc/kamailio/lb_B/kamailio.cfg: OK", out.stdout)

    output_file = base_dir.joinpath("etc/kamailio/lb_B/kamailio.cfg")
    test_file = "fixtures/output/lb_kamailio_cfg_instances_B"

    check_output(str(output_file), test_file)
    assert out.returncode == 0


def test_instances_info_noargs(helpercli, tmpdir):
    out = helpercli(
        "instances-info",
        env={
            "TEMPLATE_INSTANCES": "fixtures/repos/ngcp.instances",
            "NETWORK_CONFIG": "fixtures/repos/network_carrier_instances.yml",
        },
    )

    test_file = "fixtures/output/instances_info_noargs"
    check_stdoutput(out.stdout, test_file, tmpdir)
    assert out.returncode == 0


def test_instances_info_args(helpercli, tmpdir):
    out = helpercli(
        "instances-info",
        "/etc",
        env={
            "TEMPLATE_INSTANCES": "fixtures/repos/ngcp.instances",
            "NETWORK_CONFIG": "fixtures/repos/network_carrier_instances.yml",
        },
    )

    test_file = "fixtures/output/instances_info_args"
    check_stdoutput(out.stdout, test_file, tmpdir)
    assert out.returncode == 0


def test_instances_info_args_same(helpercli, tmpdir):
    out = helpercli(
        "instances-info",
        "/etc/kamailio/lb",
        env={
            "TEMPLATE_INSTANCES": "fixtures/repos/ngcp.instances",
            "NETWORK_CONFIG": "fixtures/repos/network_carrier_instances.yml",
        },
    )

    test_file = "fixtures/output/instances_info_args_same"
    check_stdoutput(out.stdout, test_file, tmpdir)
    assert out.returncode == 0


def test_instances_info_args_longer(helpercli, tmpdir):
    out = helpercli(
        "instances-info",
        "/etc/kamailio/lb/db",
        env={
            "TEMPLATE_INSTANCES": "fixtures/repos/ngcp.instances",
            "NETWORK_CONFIG": "fixtures/repos/network_carrier_instances.yml",
        },
    )

    test_file = "fixtures/output/instances_info_args_longer"
    check_stdoutput(out.stdout, test_file, tmpdir)
    assert out.returncode == 0


def test_instances_info_relative_path(helpercli):
    out = helpercli(
        "instances-info",
        "../lb/db",
        env={
            "TEMPLATE_INSTANCES": "fixtures/repos/ngcp.instances",
            "NETWORK_CONFIG": "fixtures/repos/network_carrier_instances.yml",
        },
    )

    assert out.returncode != 0
