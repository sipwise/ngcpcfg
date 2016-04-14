#!/usr/bin/env python

from __future__ import print_function
import copy
import io
import errno
import os
import pytest
import re
import subprocess
import sys
import unittest

command = ["fakeroot",
           "env",
           "PATH=fixtures/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin",
           "../sbin/ngcpcfg", ]


def create_prog(filename, command):
    """Create test program.

    :param unicode filename: destination filename
    :param unicode command: command to write to test program
    """
    with io.open(filename, 'w', encoding='utf-8') as fp:
        fp.write(u"#!/bin/sh\n%s\n" % (command, ))
        os.fchmod(fp.fileno(), 0o755)


def mkdir_p(path):
    """Simulate 'mkdir -p' behavior by creating a directory
    and its parent directory (if not existing yet) and
    not failing if the directory already exists:.

    :param unicode path: destination directory
    """
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class TestCommandLine(unittest.TestCase):

    def _executeAndReturnOutput(self, *args):
        self._set_environment()
        p = subprocess.Popen(self.command + list(args), stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=self.env)
        stdoutdata, stderrdata = p.communicate()
        print(stdoutdata, file=sys.stdout)
        print(stderrdata, file=sys.stderr)
        return p.returncode, stdoutdata, stderrdata

    def _set_environment(self):
        mkdir_p('./fixtures/bin/')
        create_prog("./fixtures/bin/hostname", "echo %s" %
                    self.config['HOSTNAME'])
        create_prog("./fixtures/bin/ngcp-nodename", "echo %s" %
                    self.config['NODENAME'])

    def setUp(self):
        self.command = copy.deepcopy(command)
        self.env = {
            'FUNCTIONS': '../functions/',
            'NGCPCFG': 'fixtures/repos/ngcpcfg.cfg',
            'SCRIPTS': '../scripts/',
            'HELPER': '../helper/',
        }
        self.config = {
            'HOSTNAME': 'spce',
            'NODENAME': 'spce',
        }

    def test_ngcpcfg_ko(self):
        self.env['NGCPCFG'] = '/doesnotexist'
        # self.config['HOSTNAME']='sppo'
        res = self._executeAndReturnOutput('help')
        self.assertNotEquals(res[0], 0)
        exp_regex = re.compile('Error: Could not read configuration file '
                               '/etc/ngcp-config/ngcpcfg.cfg. Exiting.')
        self.assertRegexpMatches(str(res[2]), exp_regex)

    def test_no_action_ok(self):
        res = self._executeAndReturnOutput('')
        self.assertNotEquals(res[0], 0)
        exp_regex = re.compile('.*For further usage information and '
                               'options.*', re.MULTILINE)
        self.assertRegexpMatches(str(res[2]), exp_regex)

    def test_simple_build_template_ok(self):
        res = self._executeAndReturnOutput("build",
                                           "/etc/apt/apt.conf.d/",
                                           "71_no_recommended")
        exp_regex = re.compile('.*Generating '
                               '/etc/apt/apt.conf.d/71_no_recommended: OK.*',
                               re.MULTILINE)
        self.assertRegexpMatches(str(res[1]), exp_regex)
