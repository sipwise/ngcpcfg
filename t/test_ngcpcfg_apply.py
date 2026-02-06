#!/usr/bin/env py.test-3

from pathlib import Path
import pytest
import re


def create_change(path, text="hello"):
    if not isinstance(path, Path):
        path = Path(path).resolve()
    with path.open("a") as file_object:
        # Append text at the end of file
        file_object.write(text)


@pytest.mark.apply
def test_apply_no_commit_msg(ngcpcfg, ngcpcfgcli):
    env, cfg = ngcpcfg(
        {
            "TEMPLATE_POOL_BASE": "fixtures/apply_templates",
        }
    )
    # create a change in repo
    create_change(env["NGCPCTL_MAIN"].joinpath("hello.yml"), "whatever: yes")
    out = ngcpcfgcli(
        "apply",
        env=env,
    )

    assert re.search(r"Please provide commit message", out.stdout)
    assert re.search(
        r"Error: Uncommitted configuration files found", out.stderr
    )
    assert out.returncode != 0


@pytest.mark.apply
def test_apply_no_commit_msg_options(ngcpcfg, ngcpcfgcli):
    env, cfg = ngcpcfg(
        {
            "TEMPLATE_POOL_BASE": "fixtures/apply_templates",
        }
    )
    # create a change in repo
    create_change(env["NGCPCTL_MAIN"].joinpath("hello.yml"), "whatever: yes")
    out = ngcpcfgcli(
        "apply",
        "--dry-run",
        env=env,
    )

    assert re.search(r"no explicit service state changed", out.stderr)
    assert re.search(r"skip restore-permissions", out.stderr)
    assert re.search(r"apply --dry-run", out.stderr)
    assert out.returncode == 0


@pytest.mark.apply
def test_apply_with_commit_msg(ngcpcfg, ngcpcfgcli):
    commit_msg = "whatever commit message"
    env, cfg = ngcpcfg(
        {
            "TEMPLATE_POOL_BASE": "fixtures/apply_templates",
        }
    )
    # create a change in repo
    create_change(env["NGCPCTL_MAIN"].joinpath("hello.yml"), "whatever: yes")
    out = ngcpcfgcli(
        "apply",
        commit_msg,
        env=env,
    )
    assert out.returncode == 0
    assert re.search(r"Generating .+/etc/fake.txt: OK", out.stdout)
    assert re.search(r"DEBUG: msg:\"{}\"".format(commit_msg), out.stderr)


@pytest.mark.apply
def test_apply_with_commit_msg_options(ngcpcfg, ngcpcfgcli):
    commit_msg = "whatever commit message"
    env, cfg = ngcpcfg(
        {
            "TEMPLATE_POOL_BASE": "fixtures/apply_templates",
        }
    )
    # create a change in repo
    create_change(env["NGCPCTL_MAIN"].joinpath("hello.yml"), "whatever: yes")
    out = ngcpcfgcli(
        "apply",
        "--ignore-branch-check",
        commit_msg,
        env=env,
    )
    assert out.returncode == 0

    assert re.search(r"Generating .+/etc/fake.txt: OK", out.stdout)
    assert re.search(r"DEBUG: msg:\"{}\"".format(commit_msg), out.stderr)

    assert re.search(
        r"--ignore-branch-check is enabled, not checking for branch 'master'",
        out.stdout,
    )
