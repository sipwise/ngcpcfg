#!/usr/bin/env py.test-3

import pytest

###############################################################
#  ngcpcfg get
###############################################################


@pytest.mark.get
def test_get_action_missing_key_parameter(ngcpcfgcli):
    out = ngcpcfgcli("get")
    assert "" in out.stdout
    assert "Usage: ngcpcfg get <key>" in out.stderr
    assert out.returncode == 1


@pytest.mark.get
def test_get_action_missing_file(ngcpcfgcli):
    out = ngcpcfgcli("get", "test", env={"NGCPCTL_CONFIG": "/run/nonexistent-file"})
    assert "" in out.stdout
    assert (
        "Error: Configuration file /run/nonexistent-file does not "
        + "exist (unconfigured?) - exiting."
        in out.stderr
    )
    assert out.returncode == 1


@pytest.mark.get
def test_get_wrong_get_option(ngcpcfgcli):
    out = ngcpcfgcli("get", "--something", "key.missing")
    assert "" in out.stdout
    assert "Usage: ngcpcfg get <key>" in out.stderr
    assert out.returncode == 1


@pytest.mark.get
def test_get_action_constants_child_item(ngcpcfgcli):
    out = ngcpcfgcli("get", "database.dbhost")
    assert "localhost" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.get
def test_get_action_config_child_item(ngcpcfgcli):
    out = ngcpcfgcli("get", "www_admin.fees_csv.element_order")
    assert (
        "destination zone zone_detail "
        + "onpeak_init_rate onpeak_init_interval "
        + "onpeak_follow_rate onpeak_follow_interval "
        + "offpeak_init_rate offpeak_init_interval "
        + "offpeak_follow_rate offpeak_follow_interval "
        + "use_free_time"
        in out.stdout
    )
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.get
def test_get_action_missing_item(ngcpcfgcli):
    out = ngcpcfgcli("get", "key.missing")
    assert "\n" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.get
def test_get_action_config_ha(ngcpcfgcli):
    out = ngcpcfgcli(
        "get",
        "ha.enabled",
        env={
            "NGCPCFG": "fixtures/ngcpcfg_pro.cfg",
        },
    )
    assert "yes" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.get
def test_get_action_config_pair(ngcpcfgcli):
    out = ngcpcfgcli(
        "get",
        "pair.enabled",
        env={
            "NGCPCFG": "fixtures/ngcpcfg_pro.cfg",
        },
    )
    assert "yes" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.get
def test_get_action_failure_TT154105(ngcpcfgcli):
    out = ngcpcfgcli("get", "/some/path")
    assert "" in out.stdout
    assert "Error: cannot process request for '/some/path'!" in out.stderr
    assert out.returncode == 1
