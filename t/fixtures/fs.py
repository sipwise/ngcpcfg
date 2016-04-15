#!/usr/bin/env python3

import re
import random
import string
import pytest
import os.path
import contextlib
import collections

from .commandline import run


PasswdUser = collections.namedtuple('PasswdUser',
    'password:uid:gid:info:home:shell'.split(':'))
Crontab = collections.namedtuple('Crontab',
    'm:h:dom:mon:dow:user:command'.split(':'))
Fstab = collections.namedtuple('Fstab',
    'filesystem:mountpoint:type:options:dump:fsck'.split(':'))
Group = collections.namedtuple('Group',
    'password:gid:users'.split(':'))
Host = collections.namedtuple('Host', ['ipv4', 'ipv6'])


@contextlib.contextmanager
def keep_directory():
    """Restore the current working directory when finished.

    Originally written by vincentbernat:
      https://github.com/vincentbernat/lldpd/blob/master/tests/integration/fixtures/namespaces.py
    """
    cwd = os.getcwd()
    try:
        yield
    finally:
        os.chdir(cwd)


class FileSystem:
    """Provides methods to simplify work with file system"""

    @property
    def cwd(self):
        return os.getcwd()

    def __contains__(self, path):
        return os.path.exists(path)

    @staticmethod
    def create_random_file(path, size=32):
        """Create a file with random content. `size` provided in bytes"""
        with open(path, 'xb') as fd:
            fd.write(bytes([random.randint(1, 127) for _ in range(size)]))
        return path

    @staticmethod
    def create_random_text_file(path, size=32):
        """Create a text file with random content. `size` provided in bytes"""
        alphabet = string.ascii_letters + ' .'
        with open(path, 'x') as fd:
            for _ in range(size):
                fd.write(random.choice(alphabet))
        return path

    @staticmethod
    def read_crontab_file(filepath):
        """Read crontab file, returns [Crontab]"""
        entries = []
        with open(filepath) as fd:
            for line in fd.readlines():
                # comment or empty line
                if line.startswith('#') or not line.strip():
                    continue
                # variable assignment line
                if re.match('[A-Z][A-Z0-9]+=', line):
                    continue
                entries.append(Crontab(line.split(None, 5)))
        return entries

    @staticmethod
    def read_etc_crontab():
        """Read /etc/crontab and returns [Crontab]"""
        return FileSystem.read_crontab_file('/etc/crontab')

    @staticmethod
    def read_etc_fstab():
        """Read /etc/fstab and returns [Fstab]"""
        entries = []
        with open('/etc/fstab') as fd:
            for line in fd.readlines():
                if line.startswith('#') or not line.strip():
                    continue
                entries.append(Fstab(line.strip().split(':')))
        return entries

    @staticmethod
    def read_etc_group():
        """Read /etc/group and returns [Group]"""
        groups = {}
        with open('/etc/group') as fd:
            for line in fd.readlines():
                if line.startswith('#') or not line.strip():
                    continue
                username, *others = line.split(':')
                groups[username] = Group(*others)
        return groups

    @staticmethod
    def read_etc_hosts():
        """Read /etc/hosts file. Example::

            127.0.0.1    localhost some.domain
            ::1          localhost

        returns

            {'localhost': Host(ipv4='127.0.0.1', ipv6='::1'),
             'some.domain': Host(ipv4='127.0.0.1', ipv6='')}
        """
        hosts = {}
        with open('/etc/hosts') as fd:
            for line in fd.readlines():
                if not line.strip() or line.startswith('#'):
                    continue
                names = line.split()
                if len(names) < 2:
                    raise ValueError("Line '{}' in /etc/hosts uninterpretable".format(line.strip()))
                ipv4, ipv6 = '', ''
                if ':' in names[0]:
                    ipv6 = names[0]
                else:
                    ipv4 = names[0]
                for name in names[1:]:
                    if name in hosts:
                        ipv4 = ipv4 or hosts[name].ipv4
                        ipv6 = ipv6 or hosts[name].ipv6
                    hosts[name] = Host(ipv4=ipv4, ipv6=ipv6)
        return hosts

    @staticmethod
    def read_etc_passwd():
        """Reads /etc/passwd and returns {username: PasswdUser}"""
        users = {}
        with open('/etc/passwd') as fd:
            for line in fd.readlines():
                if line.strip():
                    username, *others = line.strip().split(':')
                    users[username] = PasswdUser(*others)
        return users

    @staticmethod
    def filesize(path):
        """Return file size of `path` in bytes"""
        return os.path.getsize(path)


@pytest.fixture()
def fs():
    return FileSystem()
