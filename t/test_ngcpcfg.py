#!/usr/bin/env py.test-3

import os
import pytest
import re
from fixtures.fs import check_output


@pytest.mark.cmdline
def test_ngcpcfgcfg_ok(ngcpcfgcli):
    out = ngcpcfgcli()
    assert (
        "For further usage information and options "
        "see the ngcpcfg(8) man page" in out.stderr
    )
    assert out.returncode == 1


@pytest.mark.cmdline
def test_ngcpcfgcfg_ko(ngcpcfgcli):
    out = ngcpcfgcli(env={"NGCPCFG": "/doesnotexist"})
    assert (
        "Error: Could not read configuration file "
        "/etc/ngcp-ngcpcfg/ngcpcfg.cfg. Exiting." in out.stderr
    )
    assert out.returncode == 1


@pytest.mark.mt_16391
def test_simple_build_template_ok(ngcpcfgcli):
    out = ngcpcfgcli("build", "/etc/apt/apt.conf.d/71_no_recommended")
    assert out.returncode == 0
    regex = re.compile(
        r"Generating "
        + str(out.env["OUTPUT_DIRECTORY"])
        + r"/etc/apt/apt.conf.d/71_no_recommended: OK"
    )
    assert re.search(regex, out.stdout)


@pytest.mark.build
def test_simple_build_template_no_ha_no_carrier(ngcpcfgcli):
    out = ngcpcfgcli("build", "/etc/config_variants")
    assert out.returncode == 0
    regex = re.compile(
        r"Generating "
        + str(out.env["OUTPUT_DIRECTORY"])
        + r"/etc/config_variants: OK"
    )
    assert re.search(regex, out.stdout)
    output_file = os.path.join(
        out.env["OUTPUT_DIRECTORY"], "etc/config_variants"
    )
    test_file = "fixtures/output/config_variants"
    check_output(output_file, test_file)


@pytest.mark.build
def test_simple_build_template_pro(ngcpcfgcli):
    out = ngcpcfgcli(
        "build",
        "/etc/config_variants",
        env={
            "NGCPCFG": "fixtures/ngcpcfg_pro.cfg",
        },
    )
    assert out.returncode == 0
    regex = re.compile(
        r"Generating "
        + str(out.env["OUTPUT_DIRECTORY"])
        + r"/etc/config_variants: OK"
    )
    assert re.search(regex, out.stdout)
    output_file = os.path.join(
        out.env["OUTPUT_DIRECTORY"], "etc/config_variants"
    )
    test_file = "fixtures/output/config_variants_pro"
    check_output(output_file, test_file)


@pytest.mark.tt_17401
def test_fail_on_existing_dir_matching_output_filename(ngcpcfg, ngcpcfgcli):
    output = "/etc/apt/apt.conf.d/71_no_recommended"
    env, cfg = ngcpcfg()
    output_dir = env["OUTPUT_DIRECTORY"] / output[1:]
    output_dir.mkdir(parents=True)
    out = ngcpcfgcli(
        "build",
        output,
        env=env,
    )
    regex = re.compile(
        "Error: Generating file .*"
        + output
        + r" not possible, it\'s an existing directory."
    )
    assert re.search(regex, out.stderr)
    assert out.returncode == 1
