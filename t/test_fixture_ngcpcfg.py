#!/usr/bin/env py.test-3

import pytest
from pathlib import Path
from fixtures.programs import copy_tree
from fixtures.programs import read_cfg


def test_read_cfg():
    env = {
        "CONFIG_POOL": "/etc",
    }
    cfg = read_cfg("fixtures/ngcpcfg.cfg", env)
    cfg["ngcpcfg"]["CONFIG_POOL"] == env["CONFIG_POOL"]


def test_file_out(tmpdir):
    """src is a file from outside NGCPCTL_MAIN"""
    filename = "config.yml"
    src = Path("fixtures/repos").joinpath(filename)
    dst_dir = Path(tmpdir.mkdir("copy_tree"))
    assert copy_tree(dst_dir, src, dst_dir) is None


def test_file_in(tmpdir):
    """src is a file from NGCPCTL_MAIN"""
    filename = "config.yml"
    base = Path("fixtures/repos")
    src = base.joinpath(filename)
    dst_dir = Path(tmpdir.mkdir("copy_tree"))
    rel, dst = copy_tree(base, src, dst_dir)
    assert dst_dir.joinpath(filename).exists()
    assert str(rel) == filename
    assert dst == dst_dir.joinpath(filename)


def test_dir_out(tmpdir):
    dirname = tmpdir.mkdir("config")
    dst_dir = Path(tmpdir.mkdir("copy_tree"))
    assert copy_tree(dst_dir, dirname, dst_dir) is None


def test_dir_in(tmpdir):
    src = tmpdir.mkdir("config")
    dst_dir = Path(tmpdir.mkdir("copy_tree"))
    rel, dst = copy_tree(tmpdir, src, dst_dir)
    assert dst_dir.joinpath(src).exists()
    assert str(rel) == "config"
    assert dst == dst_dir.joinpath("config")


def test_empty(ngcpcfg):
    env, cfg = ngcpcfg()
    ngcpctl_config = Path(env["NGCPCTL_MAIN"]).joinpath("config.yml")
    assert ngcpctl_config.exists()
    assert str(ngcpctl_config) != str(cfg["NGCPCTL_CONFIG"])
    assert Path(cfg["TEMPLATE_POOL_BASE"]) == Path(
        env["NGCPCTL_MAIN"]
    ).joinpath("templates")


def test_config(ngcpcfg):
    """test that templates are properly copied and configs defined in env"""
    env, cfg = ngcpcfg({"NGCPCFG": "fixtures/ngcpcfg.cfg"})
    tt2_path = Path(cfg["TEMPLATE_POOL_BASE"]).joinpath(
        "etc/bad-syntax.txt.tt2"
    )
    assert tt2_path.exists()
    assert (
        Path(env["NETWORK_CONFIG"])
        == Path("fixtures/repos/network.yml").resolve()
    )


def test_template_pool(ngcpcfg):
    pool_path = Path("fixtures/apply_templates").resolve()
    env, cfg = ngcpcfg(
        {
            "TEMPLATE_POOL_BASE": pool_path,
        }
    )
    assert env["TEMPLATE_POOL_BASE"] == env["SERVICES_POOL_BASE"]
    tt2_path = Path(cfg["TEMPLATE_POOL_BASE"]).joinpath("etc/fake.txt.tt2")
    assert tt2_path.exists()
    # no files from fixtures/repos/templates is left
    tt2_path = Path(cfg["TEMPLATE_POOL_BASE"]).joinpath(
        "etc/bad-syntax.txt.tt2"
    )
    assert not tt2_path.exists()


def test_empty_cli(ngcpcfgcli):
    out = ngcpcfgcli(
        "status",
    )
    assert out.returncode == 0
    ngcpctl_config = Path(out.env["NGCPCTL_MAIN"]).joinpath("config.yml")
    assert ngcpctl_config.exists()
    assert str(ngcpctl_config) != str(out.cfg["NGCPCTL_CONFIG"])


def test_template_pool_cli(ngcpcfgcli):
    pool_path = Path("fixtures/apply_templates").resolve()
    out = ngcpcfgcli(
        "status",
        env={
            "TEMPLATE_POOL_BASE": pool_path,
        },
    )
    tt2_path = Path(out.cfg["TEMPLATE_POOL_BASE"]).joinpath("etc/fake.txt.tt2")
    assert tt2_path.exists()


def test_config_cli(ngcpcfgcli):
    """test that templates are properly copied and configs defined in env"""
    out = ngcpcfgcli(
        "status", env={"NGCPCFG": "fixtures/ngcpcfg_carrier_instances.cfg"}
    )
    # NGCPCFG is always generated with env values and add as
    # "${NGCPCTL_MAIN}/ngcpcfg.cfg".
    assert (
        out.env["NGCPCFG"]
        == Path(out.env["NGCPCTL_MAIN"]).joinpath("ngcpcfg.cfg").resolve()
    )
    tt2_path = Path(out.cfg["TEMPLATE_POOL_BASE"]).joinpath(
        "etc/bad-syntax.txt.tt2"
    )
    assert tt2_path.exists()
    assert (
        Path(out.env["NETWORK_CONFIG"])
        == Path("fixtures/repos/network_carrier_instances.yml").resolve()
    )
