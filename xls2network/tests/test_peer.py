#!/usr/bin/env python3

import os.path
import helpers
import tempfile
import network_xls2yml
import ruamel

testfile = os.path.splitext(__file__)[0] + '.csv'


def test_one_host():
    xls_fd = helpers.read(testfile)
    yml_fd = tempfile.TemporaryFile(mode='r+', encoding='utf-8')

    network_xls2yml.convert(xls_fd, yml_fd)

    xls_fd.close()
    yml_fd.seek(0)
    content = yml_fd.read()

    dom = ruamel.yaml.load(content, Loader=ruamel.yaml.Loader)

    assert dom['hosts']['gd01a']['peer'] == 'gd01b'
    assert dom['hosts']['gd01b']['peer'] == 'gd01a'
