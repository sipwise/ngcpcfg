#!/usr/bin/env py.test-3
import re

import pytest

CMD = "../sbin/ngcp-instances-validator"


def test_help(cli):
    cmd = [CMD, "--help"]
    out = cli(*cmd)
    assert out.exitcode == 0


def test_no_network(cli):
    cmd = [CMD]
    out = cli(*cmd)
    assert out.exitcode != 0
    assert re.search(
        "Can't open '/etc/ngcp-config/network.yml' for input", out.stderr
    )


def test_no_instances(cli):
    cmd = [CMD, "--network-file=./fixtures/repos/network_pro.yml"]
    out = cli(*cmd)
    assert out.exitcode == 0


@pytest.mark.tt_168102
def test_pro_instances(cli):
    cmd = [CMD, "--network-file=./fixtures/repos/network_pro_instances.yml"]
    out = cli(*cmd)
    assert out.exitcode == 0


def test_wrong_link(cli):
    cmd = [CMD, "--network-file=./fixtures/instances-validator/wrong_link.yml"]
    out = cli(*cmd)
    assert out.exitcode != 0
    msg = "Missing required instance for connection link"
    assert re.search(
        rf"\[instances/A/proxy/fake\] {msg}",
        out.stderr,
    )
    msg = "Missing required host for connection link"
    assert re.search(
        rf"\[instances/B/proxy/sp3\] {msg}",
        out.stderr,
    )


def test_wrong_link_interfaces(cli):
    file = "wrong_link_interfaces"
    cmd = [
        CMD,
        f"--network-file=./fixtures/instances-validator/{file}.yml",
    ]
    out = cli(*cmd)
    assert out.exitcode != 0
    msg = "Missing type sip_X on link interface"
    assert re.search(
        rf"\[instances/A/proxy/C/neth1\] {msg}",
        out.stderr,
    )
    assert re.search(
        rf"\[instances/B/proxy/sp2/neth1\] {msg}",
        out.stderr,
    )
