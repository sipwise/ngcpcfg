#!/usr/bin/env py.test-3
import re

from fixtures.fs import check_output

filepath = "etc/rtpengine{}/rtpengine.conf"
msg = r"Generating {}/{}: OK"
env = {
    "NGCP_HOSTNAME": "lb01a",
    "TEMPLATE_POOL_BASE": "fixtures/build_instances",
    "TEMPLATE_INSTANCES": "fixtures/repos/instances.yml",
    "NGCPCFG": "fixtures/ngcpcfg_carrier_instances.cfg",
    "NETWORK_CONFIG": "fixtures/repos/network_carrier_instances_rtp.yml",
}


def test_carrier_instances(ngcpcfgcli):
    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/rtpengine/rtpengine.conf",
        env=env,
    )
    rstr = msg.format(out.env["OUTPUT_DIRECTORY"], filepath.format(""))
    assert re.search(rstr, out.stdout)
    output_file = out.env["OUTPUT_DIRECTORY"].joinpath(filepath.format(""))
    test_file = "fixtures/output/rtpengine.conf_carrier"
    check_output(str(output_file), test_file)

    rstr = msg.format(out.env["OUTPUT_DIRECTORY"], filepath.format("_A"))
    assert re.search(rstr, out.stdout)
    output_file = out.env["OUTPUT_DIRECTORY"].joinpath(filepath.format("_A"))
    test_file = "fixtures/output/rtpengine.conf_instances_A"
    check_output(str(output_file), test_file)
