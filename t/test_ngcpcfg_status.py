#!/usr/bin/env py.test-3

import pytest
import re
from pathlib import Path


@pytest.mark.status
def test_status(ngcpcfgcli):
    out = ngcpcfgcli(
        "status",
    )
    assert out.returncode == 0


@pytest.mark.status
def test_status_build(ngcpcfg, ngcpcfgcli):
    env, cfg = ngcpcfg()
    new_file = Path(env["STATE_FILES_DIR"]).joinpath("build")
    new_file.write_text("hola")
    out = ngcpcfgcli("status", env=env)
    assert out.returncode == 0
    assert re.search(
        r"ACTION_NEEDED: commits without according build identified", out.stdout
    )
