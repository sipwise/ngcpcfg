import pytest
import os
import subprocess
import sys
from collections import namedtuple

ProcessResult = namedtuple(
    "ProcessResult", ["returncode", "stdout", "stderr", "outdir"]
)


@pytest.fixture()
def ngcpcfgcli(gitrepo, tmpdir, *args):
    """Execute ``ngcpcfg``."""
    code = os.path.abspath("..")
    testbin = os.path.abspath("fixtures/bin")
    fakehome = tmpdir.mkdir("fakehome")
    outdir = tmpdir.mkdir("ngcp-pytest-output")
    # testing is the git_root inside the gitrepo.default
    outdir = os.path.join(gitrepo.extract_archive(gitrepo.default, outdir), "testing")
    outdir_repo = gitrepo.in_folder(outdir)
    rundir = tmpdir.mkdir("ngcp-pytest-rundir")

    def run(*args, env={}):
        testenv = {
            "PATH": "{}:/usr/bin:/bin:/usr/sbin:/sbin".format(testbin),
            "FUNCTIONS": "{}/functions/".format(code),
            "NGCPCFG": os.path.abspath("fixtures/ngcpcfg.cfg"),
            "SCRIPTS": "{}/scripts/".format(code),
            "HELPER": "{}/helper/".format(code),
            "HOOKS": "{}/hooks/".format(code),
            "PERL5LIB": "{}/lib/".format(code),
            "NGCP_TESTSUITE": "true",
            "CONFIG_USER": "nobody",
            "CONFIG_GROUP": "root",
            "CONFIG_CHMOD": "0644",
            "CONSTANTS_CONFIG_USER": "nobody",
            "CONSTANTS_CONFIG_GROUP": "root",
            "CONSTANTS_CONFIG_CHMOD": "0644",
            "NETWORK_CONFIG_USER": "nobody",
            "NETWORK_CONFIG_GROUP": "root",
            "NETWORK_CONFIG_CHMOD": "0644",
            "NO_DB_SYNC": "true",
            "HOME": os.path.abspath(fakehome),
            "SKIP_UPDATE_PERMS": "true",
            "SKIP_RESTORE_PERMS": "true",
            "OUTPUT_DIRECTORY": outdir,
            "STATE_FILES_DIR": outdir + "/var/lib/ngcpcfg/state/",
            "RUN_DIR": str(rundir),
        }
        testenv.update(env)

        assert os.path.isdir(testenv["OUTPUT_DIRECTORY"])
        assert os.path.join(testenv["OUTPUT_DIRECTORY"], ".git")

        # if we're already running under root don't execute under fakeroot,
        # causing strange problems when debugging execution e.g. via strace
        if os.getuid() == 0:
            fakeroot = []
        else:
            fakeroot = ["fakeroot"]
        config = "{}/sbin/ngcpcfg".format(code)
        p = subprocess.Popen(
            fakeroot + [config] + list(args),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=testenv,
        )
        stdout, stderr = p.communicate(timeout=30)
        stdout, stderr = str(stdout), str(stderr)

        # debug, only printed in logs in case of error
        print("stdout:")
        print(stdout)
        print("stderr:")
        print(stderr)

        result = ProcessResult(p.returncode, stdout, stderr, outdir)
        return result

    return run
