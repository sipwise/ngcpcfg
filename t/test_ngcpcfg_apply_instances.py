#!/usr/bin/env py.test-3

from pathlib import Path
import pytest
import re
import shutil
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
            "TEMPLATE_INSTANCES": "fixtures/repos/instances.yml",
            "NGCPCFG": "fixtures/ngcpcfg_carrier_instances.cfg",
        },
    )

    assert out.returncode == 0
    assert not re.search(r"Error", out.stdout)
    assert not re.search(r"Error", out.stderr)

    base_dir = out.env["OUTPUT_DIRECTORY"]
    output_file = base_dir.joinpath("ngcpcfg.service")
    check_stdoutput("INSTANCE_NAME:\n", str(output_file), tmpdir)
    assert re.search(
        r"Executing action for .*/etc/kamailio/lb/ngcpcfg.services", out.stdout
    )

    output_file = base_dir.joinpath("ngcpcfg.serviceA")
    check_stdoutput("INSTANCE_NAME:A\n", str(output_file), tmpdir)
    assert re.search(
        r"Executing action for .*/etc/kamailio/lb/ngcpcfg.services\[A\]", out.stdout
    )

    output_file = base_dir.joinpath("ngcpcfg.serviceB")
    check_stdoutput("INSTANCE_NAME:B\n", str(output_file), tmpdir)
    assert re.search(
        r"Executing action for .*/etc/kamailio/lb/ngcpcfg.services\[B\]", out.stdout
    )


def test_apply_instances_changes(ngcpcfg, ngcpcfgcli, tmpdir, gitrepo):
    commit_msg = "instance changes for B"
    env, cfg = ngcpcfg(
        env={
            "NGCP_HOSTNAME": "lb01a",
            "TEMPLATE_POOL_BASE": "fixtures/apply_instances",
            "TEMPLATE_INSTANCES": "fixtures/repos/instances.yml",
            "NGCPCFG": "fixtures/ngcpcfg_carrier_instances.cfg",
        }
    )
    base_dir = env["OUTPUT_DIRECTORY"]
    base_git = Path(base_dir).joinpath("etc")
    base_path = Path(base_dir).joinpath("etc/kamailio")
    base_orig = Path("fixtures/output")
    orig = [
        ("lb_kamailio_cfg_carrier", "lb"),
        ("lb_kamailio_cfg_instances_A", "lb_A"),
        ("lb_kamailio_cfg_instances_B", "lb_B"),
    ]
    # put expected output of build_instances
    with gitrepo.in_folder(base_git) as git:
        # ensure we have valid user information
        git.config("--local", "user.email", "pytest@example.com")
        git.config("--local", "user.name", "pytest")
        for file, dir in orig:
            dst_path = base_path.joinpath(dir)
            dst_path.mkdir(parents=True, exist_ok=True)
            dst_file = dst_path.joinpath("kamailio.cfg")
            shutil.copy(base_orig.joinpath(file), dst_file)
            git.add(dst_file)
        ex, out, err = git.commit("-a", "-m", "old conf done")
        print("{}\nstdout:\n{}stderr:{}\n".format("git commit", out, err))
        assert ex == 0

    out = ngcpcfgcli(
        "apply",
        commit_msg,
        env=env,
    )

    assert out.returncode == 0
    assert re.search(
        r"Executing action for .*/etc/kamailio/lb/ngcpcfg.services", out.stdout
    )

    assert not re.search(r"Error", out.stdout)
    assert not re.search(r"Error", out.stderr)

    output_file = base_dir.joinpath("ngcpcfg.service")
    assert not output_file.exists()
    assert not re.search(
        r"Executing action for .*/etc/kamailio/lb/ngcpcfg.services$", out.stdout
    )

    output_file = base_dir.joinpath("ngcpcfg.serviceA")
    assert not output_file.exists()
    assert not re.search(
        r"Executing action for .*/etc/kamailio/lb/ngcpcfg.services\[A\]$", out.stdout
    )

    output_file = base_dir.joinpath("ngcpcfg.serviceB")
    check_stdoutput("INSTANCE_NAME:B\n", str(output_file), tmpdir)
    assert re.search(
        r"Executing action for .*/etc/kamailio/lb/ngcpcfg.services\[B\]", out.stdout
    )
