#!/usr/bin/env python3

import os.path
import tempfile
import network_xls2yml

inputfile = "input/sample_network_config_reduced.xlsx"
outputfile = os.path.splitext(__file__)[0] + '.yml'


def test_one_host():
    with open(inputfile, 'rb') as xls_fd:
        yml_fd = tempfile.TemporaryFile(mode='r+', encoding='utf-8')
        network_xls2yml.convert(xls_fd, yml_fd)
        yml_fd.seek(0)

    actual_content = yml_fd.read().strip().splitlines()
    print('\n'.join(actual_content))

    with open(outputfile, encoding='utf-8') as fd:
        expected_content = fd.read().strip().splitlines()

    lineno = 0
    msg = "Actual line (no. {}) '{}' differs from expected '{}'"

    for line_a, line_e in zip(actual_content, expected_content):
        lineno += 1
        assert line_a == line_e, msg.format(lineno, line_a, line_e)
