import pytest
import os
import subprocess
import sys
from collections import namedtuple


@pytest.fixture()
def ngcpcfgcli(tmpdir, *args):
    """Execute ``ngcpcfg``."""
    code = os.path.abspath("..")
    testbin = os.path.abspath('fixtures/bin')
    fakehome = tmpdir.mkdir("fakehome")

    def run(*args, env={}):
        testenv = {
            'PATH': '{}:/usr/bin:/bin:/usr/sbin:/sbin'.format(testbin),
            'FUNCTIONS': '{}/functions/'.format(code),
            'NGCPCFG': os.path.abspath('fixtures/ngcpcfg.cfg'),
            'SCRIPTS': '{}/scripts/'.format(code),
            'HELPER': '{}/helper/'.format(code),
            'HOOKS': '{}/hooks/'.format(code),
            'PERL5LIB': '{}/lib/'.format(code),
            'NGCP_TESTSUITE': 'true',
            'CONFIG_USER': 'nobody',
            'CONFIG_GROUP': 'root',
            'CONFIG_CHMOD': '0644',
            'CONSTANTS_CONFIG_USER': 'nobody',
            'CONSTANTS_CONFIG_GROUP': 'root',
            'CONSTANTS_CONFIG_CHMOD': '0644',
            'NETWORK_CONFIG_USER': 'nobody',
            'NETWORK_CONFIG_GROUP': 'root',
            'NETWORK_CONFIG_CHMOD': '0644',
            'NO_DB_SYNC': 'true',
            'HOME': os.path.abspath(fakehome),
        }
        testenv.update(env)

        # if we're already running under root don't execute under fakeroot,
        # causing strange problems when debugging execution e.g. via strace
        if os.getuid() == 0:
            fakeroot = []
        else:
            fakeroot = ['fakeroot']
        config = '{}/sbin/ngcpcfg'.format(code)

        p = subprocess.Popen(fakeroot + [config] + list(args),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=testenv)
        stdout, stderr = p.communicate(timeout=30)
        stdout, stderr = str(stdout), str(stderr)
        result = namedtuple('ProcessResult',
                            ['returncode', 'stdout', 'stderr'])(
                                p.returncode, stdout, stderr)
        return result

    return run
