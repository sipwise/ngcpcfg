#!/usr/bin/env py.test-3
import re

from fixtures.fs import check_output

msg = r"Generating {}/etc/kamailio/lb{}/whatever.cfg: OK"


def test_carrier_instances(ngcpcfgcli):
    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/kamailio/lb/whatever.cfg",
        env={
            "NGCP_HOSTNAME": "lb01a",
            "TEMPLATE_POOL_BASE": "fixtures/build_instances",
            "TEMPLATE_INSTANCES": "fixtures/repos/instances.yml",
            "NGCPCFG": "fixtures/ngcpcfg_carrier_instances.cfg",
        },
    )
    assert re.search(msg.format(out.env["OUTPUT_DIRECTORY"], ""), out.stdout)
    output_file = out.env["OUTPUT_DIRECTORY"].joinpath(
        "etc/kamailio/lb/whatever.cfg"
    )
    test_file = "fixtures/output/whatever.cfg_carrier"
    check_output(str(output_file), test_file)

    assert re.search(msg.format(out.env["OUTPUT_DIRECTORY"], "_A"), out.stdout)
    output_file = out.env["OUTPUT_DIRECTORY"].joinpath(
        "etc/kamailio/lb_A/whatever.cfg"
    )
    test_file = "fixtures/output/whatever.cfg_carrier_instances_A"
    check_output(str(output_file), test_file)

    assert re.search(msg.format(out.env["OUTPUT_DIRECTORY"], "_B"), out.stdout)
    output_file = out.env["OUTPUT_DIRECTORY"].joinpath(
        "etc/kamailio/lb_B/whatever.cfg"
    )
    test_file = "fixtures/output/whatever.cfg_carrier_instances_B"
    check_output(str(output_file), test_file)


def test_pro_instances(ngcpcfgcli):
    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/kamailio/lb/whatever.cfg",
        env={
            "NGCP_HOSTNAME": "sp1",
            "TEMPLATE_POOL_BASE": "fixtures/build_instances",
            "TEMPLATE_INSTANCES": "fixtures/repos/instances.yml",
            "NGCPCFG": "fixtures/ngcpcfg_pro_instances.cfg",
        },
    )
    assert re.search(msg.format(out.env["OUTPUT_DIRECTORY"], ""), out.stdout)
    output_file = out.env["OUTPUT_DIRECTORY"].joinpath(
        "etc/kamailio/lb/whatever.cfg"
    )
    test_file = "fixtures/output/whatever.cfg_pro"
    check_output(str(output_file), test_file)

    assert re.search(msg.format(out.env["OUTPUT_DIRECTORY"], "_A"), out.stdout)
    output_file = out.env["OUTPUT_DIRECTORY"].joinpath(
        "etc/kamailio/lb_A/whatever.cfg"
    )
    test_file = "fixtures/output/whatever.cfg_pro_instances_A"
    check_output(str(output_file), test_file)

    assert re.search(msg.format(out.env["OUTPUT_DIRECTORY"], "_B"), out.stdout)
    output_file = out.env["OUTPUT_DIRECTORY"].joinpath(
        "etc/kamailio/lb_B/whatever.cfg"
    )
    test_file = "fixtures/output/whatever.cfg_pro_instances_B"
    check_output(str(output_file), test_file)
