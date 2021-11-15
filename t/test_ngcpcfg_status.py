#!/usr/bin/env py.test-3

import os
import pytest


@pytest.mark.status
def test_status(ngcpcfgcli, tmpdir, gitrepo):
    src = "basic-ngcp-config.tar.gz"
    with gitrepo.from_archive(src):
        cfg_dir = os.path.join(gitrepo.localpath, "ngcp-config")
        out = ngcpcfgcli(
            "status",
            env={
                "NGCPCTL_MAIN": cfg_dir,
                # we just need a clean git repo
                "NGCPCTL_BASE": cfg_dir,
            },
        )
    assert out.returncode == 0
