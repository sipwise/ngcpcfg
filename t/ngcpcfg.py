#!/usr/bin/env python

from __future__ import print_function
import copy
import os
import re
import subprocess
import sys
import unittest

command = ["fakeroot",
           "env",
           "PATH=t/fixtures/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin",
           "./sbin/ngcpcfg", ]


def create_prog(filename, command):
    os.system('echo "#!/bin/sh" > %s' % filename)
    os.system('echo "%s" >> "%s"' % (command, filename))
    os.system('chmod +x %s' % filename)


class TestCommandLine(unittest.TestCase):

    def _executeAndReturnOutput(self):
        self._set_environment()
        p = subprocess.Popen(self.command, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=self.env)
        stdoutdata, stderrdata = p.communicate()
        print(stdoutdata, file=sys.stdout)
        print(stderrdata, file=sys.stderr)
        return p.returncode, stdoutdata, stderrdata

    def _set_environment(self):
        create_prog("./t/fixtures/bin/hostname", "echo %s" %
                    self.config['HOSTNAME'])
        create_prog("./t/fixtures/bin/ngcp-nodename", "echo %s" %
                    self.config['NODENAME'])

    def setUp(self):
        self.command = copy.deepcopy(command)
        self.env = {
            'FUNCTIONS': 'functions/',
            'NGCPCFG': 'ngcpcfg.cfg',  # note: this referes to t/fixtures/
            'SCRIPTS': 'scripts/',
        }
        self.config = {
            'HOSTNAME': 'spce',
            'NODENAME': 'spce',
        }

    def test_ngcpcfg_ko(self):
        self.env['NGCPCFG'] = '/doesnotexist'
        # self.config['HOSTNAME']='sppo'
        res = self._executeAndReturnOutput()
        self.assertNotEquals(res[0], 0)
        self.assertRegexpMatches(res[2],
                                 "Error: Could not read configuration file "
                                 "/etc/ngcp-config/ngcpcfg.cfg. Exiting.")

    def test_no_action_ok(self):
        res = self._executeAndReturnOutput()
        self.assertNotEquals(res[0], 0)
        expected_regex = re.compile(".*For further usage information and "
                                    "options.*", re.MULTILINE)
        self.assertRegexpMatches(res[2], expected_regex)
