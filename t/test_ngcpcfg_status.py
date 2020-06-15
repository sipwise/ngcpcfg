#!/usr/bin/env py.test-3

import os
import pytest
import re


@pytest.mark.status
def test_status(ngcpcfgcli, tmpdir, gitrepo):
    src = 'basic-ngcp-config.tar.gz'
    with gitrepo.from_archive(src):
        cfg_dir = os.path.join(gitrepo.localpath, 'ngcp-config')
        out = ngcpcfgcli("status",
                         env={
                            # don't mess with perms
                            'SKIP_RESTORE_PERMS': 'true',
                            'NGCPCTL_MAIN': cfg_dir,
                            # we just need a clean git repo
                            'NGCPCTL_BASE': cfg_dir,
                         })

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout.replace("\\n", "\n"))
    print("stderr:")
    print(out.stderr.replace("\\n", "\n"))
    assert out.returncode == 0


@pytest.mark.status
def test_status_update_process(ngcpcfgcli, tmpdir, gitrepo):
    src = 'basic-ngcp-config.tar.gz'
    with gitrepo.from_archive(src):
        cfg_dir = os.path.join(gitrepo.localpath, 'ngcp-config')
        out = ngcpcfgcli("status", "--update-process",
                         env={
                            # don't mess with perms
                            'SKIP_RESTORE_PERMS': 'true',
                            'NGCPCTL_MAIN': cfg_dir,
                            # we just need a clean git repo
                            'NGCPCTL_BASE': cfg_dir,
                         })

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout.replace("\\n", "\n"))
    print("stderr:")
    print(out.stderr.replace("\\n", "\n"))
    assert out.returncode == 0
    assert re.search(
        'Ignoring build --update-process option is enabled', out.stdout)
