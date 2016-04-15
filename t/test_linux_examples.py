#!/usr/bin/env py.test-3

import os
import pytest


def test_etc_passwd(fs):
    for user, data in fs.read_etc_passwd().items():
        print(user, data.password, data.uid, data.gid, data.info, data.home, data.shell)
    assert 'root' in fs.read_etc_passwd()

def test_etc_hosts(fs):
    for domain, host in fs.read_etc_hosts().items():
        print(domain, host.ipv4, host.ipv6)
    assert 'localhost' in fs.read_etc_hosts()

def test_etc_group(fs):
    for group, data in fs.read_etc_group().items():
        print(group, data.password, data.gid, data.users)
    assert 'root' in fs.read_etc_group()

def test_etc_fstab(fs):
    for entry in fs.read_etc_fstab():
        print(entry.filesystem, entry.mountpoint, entry.type, entry.options, entry.dump, entry.fsck)
    #assert any(entry.options == 'swap' for entry in fs.read_etc_fstab())

## crontab does not exist in Docker's debian jessie
#def test_crontab_file(fs):
#    for entry in fs.read_etc_crontab():
#        print(entry.m, entry.h, entry.dom, entry.mon, entry.dow, entry.user, entry.command)
#    assert len(fs.read_etc_crontab(filepath)) > 0

def test_random_text_file(fs):
    tmpfile = fs.create_random_text_file('0quergkjn9fryua09sfdqk3wrn', size=1023)
    assert tmpfile in fs
    assert fs.filesize(tmpfile) == 1023
    os.unlink(tmpfile)

def test_random_file(fs):
    tmpfile = fs.create_random_file('0293urkndsf092734jnbasdlkj', size=4022)
    assert tmpfile in fs
    assert fs.filesize(tmpfile) == 4022
    os.unlink(tmpfile)

...
