#!/usr/bin/env py.test-3

import pytest
from fixtures.fs import check_output, check_stdoutput

###############################################################
#  ngcpcfg cat
###############################################################


@pytest.mark.cat
def test_cat_action_unknown_config_type(ngcpcfgcli):
    out = ngcpcfgcli("cat", "mysterious")
    assert "" in out.stdout
    assert "Error: unknown config type 'mysterious'" in out.stderr
    assert out.returncode == 1


@pytest.mark.cat
def test_cat_action_wrong_get_option(ngcpcfgcli):
    out = ngcpcfgcli("cat", "--something")
    assert "" in out.stdout
    assert "Error: unknown config type '--something'" in out.stderr
    assert out.returncode == 1


@pytest.mark.cat
def test_cat_action_missing_file(ngcpcfgcli):
    out = ngcpcfgcli("cat", env={"NGCPCTL_CONFIG": "/run/nonexistent-file"})
    assert "" in out.stdout
    assert (
        "Error: Configuration file /run/nonexistent-file does not "
        + "exist (unconfigured?) - exiting."
        in out.stderr
    )
    assert out.returncode == 1


@pytest.mark.cat
def test_cat_action_config(ngcpcfgcli, tmpdir):
    out = ngcpcfgcli("cat", "config")

    test_file = "fixtures/output/config_cat_config"
    check_stdoutput(out.stdout, test_file, tmpdir)

    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.cat
def test_cat_action_config_constants(ngcpcfgcli, tmpdir):
    out = ngcpcfgcli("cat", "config", "constants")

    test_file = "fixtures/output/config_cat_config_constants"
    check_stdoutput(out.stdout, test_file, tmpdir)

    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.cat
def test_cat_action_constants_config(ngcpcfgcli, tmpdir):
    out = ngcpcfgcli("cat", "constants", "config")

    test_file = "fixtures/output/config_cat_config_constants"
    check_stdoutput(out.stdout, test_file, tmpdir)

    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.cat
def test_cat_action_config_pro(ngcpcfgcli, tmpdir):
    out = ngcpcfgcli(
        "cat",
        "config",
        env={
            "NGCPCFG": "fixtures/ngcpcfg_pro.cfg",
        },
    )

    test_file = "fixtures/output/config_cat_config_pro"
    check_stdoutput(out.stdout, test_file, tmpdir)

    assert "" in out.stderr
    assert out.returncode == 0
