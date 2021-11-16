#!/usr/bin/env py.test-3

import os
import pytest
import re


def create_change(file):
    with open(file, "a") as file_object:
        # Append 'hello' at the end of file
        file_object.write("hello")


@pytest.mark.apply
def test_apply_no_commit_msg(ngcpcfgcli, tmpdir, gitrepo):
    src = "basic-ngcp-config.tar.gz"
    with gitrepo.from_archive(src):
        cfg_dir = os.path.join(gitrepo.localpath, "ngcp-config")
        tt2_dir = os.path.join(os.getcwd(), "fixtures", "apply_templates")
        env = {
            "DEBUG": "true",
            "TEMPLATE_POOL_BASE": tt2_dir,
            "NGCPCTL_MAIN": cfg_dir,
            # we just need a clean git repo
            "NGCPCTL_BASE": cfg_dir,
        }
        # create a change in repo
        create_change(os.path.join(cfg_dir, "config.yml"))
        print("env:{}".format(env))
        out = ngcpcfgcli(
            "apply",
            env=env,
        )

    msg = r"Please provide commit message"
    regex = re.compile(msg)

    assert re.search(regex, out.stdout)
    assert out.returncode != 0


@pytest.mark.apply
def test_apply_no_commit_msg_options(ngcpcfgcli, tmpdir, gitrepo):
    src = "basic-ngcp-config.tar.gz"
    with gitrepo.from_archive(src):
        cfg_dir = os.path.join(gitrepo.localpath, "ngcp-config")
        tt2_dir = os.path.join(os.getcwd(), "fixtures", "apply_templates")
        env = {
            "DEBUG": "true",
            "TEMPLATE_POOL_BASE": tt2_dir,
            "NGCPCTL_MAIN": cfg_dir,
            # we just need a clean git repo
            "NGCPCTL_BASE": cfg_dir,
        }
        # create a change in repo
        create_change(os.path.join(cfg_dir, "config.yml"))
        print("env:{}".format(env))
        out = ngcpcfgcli(
            "apply",
            "--ignore-branch-check",
            "--dry-run",
            env=env,
        )

    msg = r"Please provide commit message"
    regex = re.compile(msg)
    assert re.search(regex, out.stdout)

    assert out.returncode != 0


@pytest.mark.apply
def test_apply_with_commit_msg(ngcpcfgcli, tmpdir, gitrepo):
    src = "basic-ngcp-config.tar.gz"
    commit_msg = "whatever commit message"
    with gitrepo.from_archive(src):
        cfg_dir = os.path.join(gitrepo.localpath, "ngcp-config")
        tt2_dir = os.path.join(os.getcwd(), "fixtures", "apply_templates")
        env = {
            "DEBUG": "true",
            "TEMPLATE_POOL_BASE": tt2_dir,
            "NGCPCTL_MAIN": cfg_dir,
            # we just need a clean git repo
            "NGCPCTL_BASE": cfg_dir,
        }
        # create a change in repo
        create_change(os.path.join(cfg_dir, "hello.yml"))
        out = ngcpcfgcli(
            "apply",
            commit_msg,
            env=env,
        )
    msg = r"Generating .+/etc/fake.txt: OK"
    regex = re.compile(msg)

    assert out.returncode == 0
    assert re.search(regex, out.stdout)

    msg = r"DEBUG: msg:\"{}\"".format(commit_msg)
    regex = re.compile(msg)
    assert re.search(regex, out.stderr)


@pytest.mark.apply
def test_apply_with_commit_msg_options(ngcpcfgcli, tmpdir, gitrepo):
    src = "basic-ngcp-config.tar.gz"
    commit_msg = "whatever commit message"
    with gitrepo.from_archive(src):
        cfg_dir = os.path.join(gitrepo.localpath, "ngcp-config")
        tt2_dir = os.path.join(os.getcwd(), "fixtures", "apply_templates")
        env = {
            "DEBUG": "true",
            "TEMPLATE_POOL_BASE": tt2_dir,
            "NGCPCTL_MAIN": cfg_dir,
            # we just need a clean git repo
            "NGCPCTL_BASE": cfg_dir,
        }
        # create a change in repo
        create_change(os.path.join(cfg_dir, "hello.yml"))
        out = ngcpcfgcli(
            "apply",
            "--dry-run",
            "--ignore-branch-check",
            commit_msg,
            env=env,
        )

    msg = r"Generating .+/etc/fake.txt: OK"
    regex = re.compile(msg)

    assert out.returncode == 0
    assert re.search(regex, out.stdout)

    msg = r"DEBUG: DRYRUN = true"
    regex = re.compile(msg)
    assert re.search(regex, out.stderr)

    msg = r"--ignore-branch-check is enabled, not checking for branch 'master'"
    regex = re.compile(msg)
    assert re.search(regex, out.stdout)

    msg = r"DEBUG: msg:\"{}\"".format(commit_msg)
    regex = re.compile(msg)
    assert re.search(regex, out.stderr)
