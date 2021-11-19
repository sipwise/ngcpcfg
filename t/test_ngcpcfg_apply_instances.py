#!/usr/bin/env py.test-3

from pathlib import Path
import pytest
import re
from fixtures.fs import check_stdoutput


def test_apply_instances(ngcpcfgcli, tmpdir):
    commit_msg = "instance changes"
    out = ngcpcfgcli(
        "apply",
        "--force-all-services",
        commit_msg,
        env={
            "NGCP_HOSTNAME": "lb01a",
            "TEMPLATE_POOL_BASE": "fixtures/build_instances",
            "TEMPLATE_INSTANCES": "fixtures/repos/ngcp.instances",
            "NGCPCFG": "fixtures/ngcpcfg_carrier_instances.cfg",
        },
    )

    assert out.returncode == 0
    assert re.search(r"Executing action for .*/etc/kamailio/lb/ngcpcfg.services", out.stdout)

    assert not re.search(r"Error", out.stdout)
    assert not re.search(r"Error", out.stderr)

    base_dir = out.env["OUTPUT_DIRECTORY"]
    output_file = base_dir.joinpath("ngcpcfg.service")
    check_stdoutput("INSTANCE_NAME:\n", str(output_file), tmpdir)

    output_file = base_dir.joinpath("ngcpcfg.serviceA")
    check_stdoutput("INSTANCE_NAME:A\n", str(output_file), tmpdir)

    output_file = base_dir.joinpath("ngcpcfg.serviceB")
    check_stdoutput("INSTANCE_NAME:B\n", str(output_file), tmpdir)