import pytest
import subprocess
import sys
from collections import namedtuple


@pytest.fixture()
def ngcpcfgcli(tmpdir, *args):
    """Execute ``ngcpcfg``."""

    def run(*args, env={}):
        testenv = {
            'PATH':      'fixtures/bin:/usr/bin:/bin:/usr/sbin:/sbin',
            'FUNCTIONS': '../functions/',
            'NGCPCFG':   'fixtures/ngcpcfg.cfg',
            'SCRIPTS':   '../scripts/',
            'HELPER':    '../helper/',
        }
        testenv.update(env)

        p = subprocess.Popen(['fakeroot'] + ['../sbin/ngcpcfg'] + list(args),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=testenv)
        stdout, stderr = p.communicate(timeout=30)
        result = namedtuple('ProcessResult',
                            ['returncode', 'stdout', 'stderr'])(
                                p.returncode, stdout, stderr)
        return result

    return run
