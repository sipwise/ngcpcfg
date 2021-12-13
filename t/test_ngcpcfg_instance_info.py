#!/usr/bin/env py.test-3

from pathlib import Path
import pytest
import re
from fixtures.fs import check_stdoutput


def test_instance_info_noargs(helpercli):
    out = helpercli(
        "instance-info",
        env={
            "NETWORK_CONFIG": "fixtures/repos/network_carrier_instances.yml",
        },
    )
    assert out.returncode != 0
    assert "Error: wrong number of arguments" in out.stderr


def test_instances_info_no_instance(helpercli):
    out = helpercli(
        "instance-info",
        "C",
        env={
            "NETWORK_CONFIG": "fixtures/repos/network_carrier_instances.yml",
        },
    )
    assert out.returncode != 0


def test_instance_info(helpercli, tmpdir):
    out = helpercli(
        "instance-info",
        "A",
        env={
            "NETWORK_CONFIG": "fixtures/repos/network_carrier_instances.yml",
        },
    )

    test_file = "fixtures/output/instance_info_A"
    assert out.returncode == 0
    check_stdoutput(out.stdout, test_file, tmpdir)
