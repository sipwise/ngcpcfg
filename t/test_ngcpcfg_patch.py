#!/usr/bin/env py.test-3

import os
import pytest
import re
import tempfile


@pytest.mark.tt_24920
def test_patch_action_no_args(ngcpcfgcli, tmpdir):
    out = ngcpcfgcli("patch",
                     env={
                         'NGCP_PORTFILE': '/tmp/ngcpcfg.port',
                         })
    string = r"Patch operation has finished successfully."
    assert string in out.stdout


@pytest.mark.tt_24920
def test_patch_action_generate_customtt_via_patch_file(ngcpcfgcli, tmpdir):
    template_path = tmpdir.join('/etc')
    apt_path = template_path.join('/apt/apt.conf.d')
    os.makedirs(str(apt_path), exist_ok=True)

    tt2 = apt_path.join('71_no_recommended.tt2')
    tt2.write('''
APT::Install-Recommends "0";
''')

    patchtt = apt_path.join("71_no_recommended.patchtt.tt2")
    patchtt.write('''
--- 71_no_recommended.tt2.orig  2017-12-08 13:31:49.763402557 +0100
+++ 71_no_recommended.tt2       2017-12-08 13:32:00.559382702 +0100
@@ -1,2 +1 @@
-
-APT::Install-Recommends "0";
+APT::Install-Recommends "1";
''')
    out = ngcpcfgcli("patch",
                     "/etc/apt/apt.conf.d/",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'NGCP_PORTFILE': '/tmp/ngcpcfg.port',
                         'OUTPUT_DIRECTORY': str(tmpdir),
                         'TEMPLATE_POOL_BASE': str(tmpdir),
                         'CONFIG_POOL': '/etc',
                         })

    assert 'Validating patch' in out.stdout
    assert '71_no_recommended.customtt.tt2' in out.stdout
    assert 'Patch operation has finished successfully.' in out.stdout

    generated_customtt = str(tmpdir) + \
        '/etc/apt/apt.conf.d/71_no_recommended.customtt.tt2'

    assert os.path.isfile(generated_customtt)
    with open(generated_customtt) as customtt:
        customtt_output = customtt.read()
    assert customtt_output == '''APT::Install-Recommends "1";\n'''


@pytest.mark.tt_24920
def test_patch_action_customtt_does_not_trigger_patch_file(ngcpcfgcli, tmpdir):
    template_path = tmpdir.join('/etc')
    apt_path = template_path.join('/apt/apt.conf.d')
    os.makedirs(str(apt_path), exist_ok=True)

    tt2 = apt_path.join('71_no_recommended.tt2')
    tt2.write('''
APT::Install-Recommends "0";
''')

    expected_output = '''
# generated via customtt without patch file
APT::Install-Recommends "1";
'''

    customtt = apt_path.join("71_no_recommended.customtt.tt2")
    customtt.write(expected_output)

    out = ngcpcfgcli("build", "--ignore-branch-check",
                     "/etc/apt/apt.conf.d/",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'NGCP_PORTFILE': '/tmp/ngcpcfg.port',
                         'OUTPUT_DIRECTORY': str(tmpdir) + "/output",
                         'TEMPLATE_POOL_BASE': str(tmpdir),
                         'CONFIG_POOL': '/etc',
                         })

    assert 'Patch operation has finished successfully.' in out.stdout
    assert 'Generating ' in out.stdout
    assert '/etc/apt/apt.conf.d/71_no_recommended: OK' in out.stdout
    assert 'Validating patch' not in out.stdout
    assert '71_no_recommended.customtt.tt2' not in out.stdout

    generated_config = str(tmpdir) + "/output" + str(tmpdir) + \
        '/etc/apt/apt.conf.d/71_no_recommended'

    assert os.path.isfile(generated_config)
    with open(generated_config) as output_file:
        output = output_file.read()
    assert output == expected_output
    # assert 0, out
