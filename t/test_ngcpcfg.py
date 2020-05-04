#!/usr/bin/env py.test-3

import filecmp
import os
import pytest
import re
import tempfile


@pytest.mark.cmdline
def test_ngcpcfgcfg_ok(ngcpcfgcli):
    out = ngcpcfgcli()
    assert 'For further usage information and options ' \
           'see the ngcpcfg(8) man page' in out.stderr


@pytest.mark.cmdline
def test_ngcpcfgcfg_ko(ngcpcfgcli):
    out = ngcpcfgcli(env={'NGCPCFG': '/doesnotexist'})
    assert 'Error: Could not read configuration file ' \
           '/etc/ngcp-config/ngcpcfg.cfg. Exiting.' in out.stderr


# NOTE - this one fails if the *main* ngcpcfg.git is not
# standing on master branch, therefore use --ignore-branch-check
# until we've a mock/fixture for it
@pytest.mark.mt_16391
def test_simple_build_template_ok(ngcpcfgcli):
    tmpdir = tempfile.mkdtemp(prefix='ngcp-', suffix='-pytest-output')
    out = ngcpcfgcli("build", "--ignore-branch-check",
                     "/etc/apt/apt.conf.d/71_no_recommended",
                     env={
                         'OUTPUT_DIRECTORY': tmpdir,
                         })
    regex = re.compile(r"Generating " +
                       tmpdir +
                       r"/etc/apt/apt.conf.d/71_no_recommended: OK")
    assert re.search(regex, out.stdout)


@pytest.mark.build
def test_simple_build_template_no_ha_no_carrier(ngcpcfgcli):
    tmpdir = tempfile.mkdtemp(prefix='ngcp-', suffix='-pytest-output')
    out = ngcpcfgcli("build", "--ignore-branch-check", "/etc/config_variants",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'OUTPUT_DIRECTORY': tmpdir,
                         })
    regex = re.compile(r"Generating " + tmpdir + r"/etc/config_variants: OK")
    assert re.search(regex, out.stdout)
    output_file = os.path.join(tmpdir, "etc/config_variants")
    test_file = "fixtures/output/config_variants"
    assert os.path.exists(output_file)
    assert os.path.exists(test_file)
    assert filecmp.cmp(output_file, test_file)


@pytest.mark.build
def test_simple_build_template_pro(ngcpcfgcli):
    tmpdir = tempfile.mkdtemp(prefix='ngcp-', suffix='-pytest-output')
    out = ngcpcfgcli("build", "--ignore-branch-check",
                     "/etc/config_variants",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'OUTPUT_DIRECTORY': tmpdir,
                         'NGCPCFG':   'fixtures/ngcpcfg_pro.cfg',
                         })
    regex = re.compile(r"Generating " + tmpdir + r"/etc/config_variants: OK")
    assert re.search(regex, out.stdout)
    output_file = os.path.join(tmpdir, "etc/config_variants")
    test_file = "fixtures/output/config_variants_pro"
    assert os.path.exists(output_file)
    assert os.path.exists(test_file)
    assert filecmp.cmp(output_file, test_file)


@pytest.mark.tt_17401
def test_fail_on_existing_dir_matching_output_filename(ngcpcfgcli, tmpdir):
    tmpdir = tempfile.mkdtemp(prefix='ngcp-', suffix='-pytest-output')
    output = "/etc/apt/apt.conf.d/71_no_recommended"
    os.makedirs(tmpdir + output)
    out = ngcpcfgcli("build", "--ignore-branch-check", output,
                     env={
                         'OUTPUT_DIRECTORY': tmpdir,
                         })
    regex = re.compile("Error: Generating file " +
                       tmpdir + output +
                       r" not possible, it\'s an existing directory.")
    assert re.search(regex, out.stderr)
    assert out.returncode == 1
