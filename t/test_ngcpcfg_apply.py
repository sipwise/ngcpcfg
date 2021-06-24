#!/usr/bin/env py.test-3

import os
import pytest
import re
from pathlib import Path


@pytest.mark.apply
def test_apply_no_commit_msg(ngcpcfgcli, tmpdir, gitrepo):
    outdir = tmpdir.mkdir("ngcp-pytest-output")
    src = "basic-ngcp-config.tar.gz"
    with gitrepo.from_archive(src):
        cfg_dir = os.path.join(gitrepo.localpath, "ngcp-config")
        tt2_dir = os.path.join(os.getcwd(), "fixtures", "apply_templates")
        env = {
            "DEBUG": "true",
            "RUN_DIR": tmpdir.mkdir("ngcp-pytest-rundir"),
            "OUTPUT_DIRECTORY": outdir,
            "TEMPLATE_POOL_BASE": tt2_dir,
            # don't mess with perms
            "SKIP_RESTORE_PERMS": "true",
            "NGCPCTL_MAIN": cfg_dir,
            # we just need a clean git repo
            "NGCPCTL_BASE": cfg_dir,
            "STATE_FILES_DIR": outdir + "/var/lib/ngcpcfg/state/",
        }
        # create a change in repo
        Path(os.path.join(cfg_dir, "config.yml")).touch()
        print("env:{}".format(env))
        out = ngcpcfgcli(
            "apply",
            env=env,
        )

    msg = r"Please provide commit message"
    regex = re.compile(msg)

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout.replace("\\n", "\n"))
    print("stderr:")
    print(out.stderr.replace("\\n", "\n"))

    assert re.search(regex, out.stdout)
    assert out.returncode != 0


@pytest.mark.apply
def test_apply_no_commit_msg_options(ngcpcfgcli, tmpdir, gitrepo):
    outdir = tmpdir.mkdir("ngcp-pytest-output")
    src = "basic-ngcp-config.tar.gz"
    with gitrepo.from_archive(src):
        cfg_dir = os.path.join(gitrepo.localpath, "ngcp-config")
        tt2_dir = os.path.join(os.getcwd(), "fixtures", "apply_templates")
        env = {
            "DEBUG": "true",
            "RUN_DIR": tmpdir.mkdir("ngcp-pytest-rundir"),
            "OUTPUT_DIRECTORY": outdir,
            "TEMPLATE_POOL_BASE": tt2_dir,
            # don't mess with perms
            "SKIP_RESTORE_PERMS": "true",
            "NGCPCTL_MAIN": cfg_dir,
            # we just need a clean git repo
            "NGCPCTL_BASE": cfg_dir,
            "STATE_FILES_DIR": outdir + "/var/lib/ngcpcfg/state/",
        }
        # create a change in repo
        Path(os.path.join(cfg_dir, "config.yml")).touch()
        print("env:{}".format(env))
        out = ngcpcfgcli(
            "apply",
            "--ignore-branch-check",
            "--dry-run",
            env=env,
        )

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout.replace("\\n", "\n"))
    print("stderr:")
    print(out.stderr.replace("\\n", "\n"))

    msg = r"Please provide commit message"
    regex = re.compile(msg)
    assert re.search(regex, out.stdout)

    assert out.returncode != 0


@pytest.mark.apply
def test_apply_with_commit_msg(ngcpcfgcli, tmpdir, gitrepo):
    outdir = tmpdir.mkdir("ngcp-pytest-output")
    src = "basic-ngcp-config.tar.gz"
    commit_msg = "whatever commit message"
    with gitrepo.from_archive(src):
        cfg_dir = os.path.join(gitrepo.localpath, "ngcp-config")
        tt2_dir = os.path.join(os.getcwd(), "fixtures", "apply_templates")
        env = {
            "DEBUG": "true",
            "RUN_DIR": tmpdir.mkdir("ngcp-pytest-rundir"),
            "OUTPUT_DIRECTORY": outdir,
            "TEMPLATE_POOL_BASE": tt2_dir,
            # don't mess with perms
            "SKIP_RESTORE_PERMS": "true",
            "NGCPCTL_MAIN": cfg_dir,
            # we just need a clean git repo
            "NGCPCTL_BASE": cfg_dir,
            "STATE_FILES_DIR": outdir + "/var/lib/ngcpcfg/state/",
        }
        print("env:{}".format(env))
        out = ngcpcfgcli(
            "apply",
            commit_msg,
            env=env,
        )

    msg = r"Generating .+/etc/fake.txt: OK"
    regex = re.compile(msg)

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout.replace("\\n", "\n"))
    print("stderr:")
    print(out.stderr.replace("\\n", "\n"))

    assert out.returncode == 0
    assert re.search(regex, out.stdout)

    msg = r"DEBUG: msg:\"{}\"".format(commit_msg)
    regex = re.compile(msg)
    assert re.search(regex, out.stderr)


@pytest.mark.apply
def test_apply_with_commit_msg_options(ngcpcfgcli, tmpdir, gitrepo):
    outdir = tmpdir.mkdir("ngcp-pytest-output")
    src = "basic-ngcp-config.tar.gz"
    commit_msg = "whatever commit message"
    with gitrepo.from_archive(src):
        cfg_dir = os.path.join(gitrepo.localpath, "ngcp-config")
        tt2_dir = os.path.join(os.getcwd(), "fixtures", "apply_templates")
        env = {
            "DEBUG": "true",
            "RUN_DIR": tmpdir.mkdir("ngcp-pytest-rundir"),
            "OUTPUT_DIRECTORY": outdir,
            "TEMPLATE_POOL_BASE": tt2_dir,
            # don't mess with perms
            "SKIP_RESTORE_PERMS": "true",
            "NGCPCTL_MAIN": cfg_dir,
            # we just need a clean git repo
            "NGCPCTL_BASE": cfg_dir,
            "STATE_FILES_DIR": outdir + "/var/lib/ngcpcfg/state/",
        }
        print("env:{}".format(env))
        out = ngcpcfgcli(
            "apply",
            "--dry-run",
            "--ignore-branch-check",
            commit_msg,
            env=env,
        )

    msg = r"Generating .+/etc/fake.txt: OK"
    regex = re.compile(msg)

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout.replace("\\n", "\n"))
    print("stderr:")
    print(out.stderr.replace("\\n", "\n"))

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
