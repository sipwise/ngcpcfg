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
    string = r"No patchtt files found, nothing to patch."
    assert string in out.stdout
    assert out.stderr == "b''"


@pytest.mark.tt_24920
def test_patch_action_generate_customtt_via_patchtt_file(ngcpcfgcli, tmpdir):
    # ensure 'ngcpcfg patch' works in the most simple case

    template_path = tmpdir.join('/etc')
    apt_path = template_path.join('/apt/apt.conf.d')
    os.makedirs(str(apt_path), exist_ok=True)

    apt_path.join('71_no_recommended.tt2').write('''
APT::Install-Recommends "0";
''')

    apt_path.join("71_no_recommended.patchtt.tt2").write('''
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

    assert "Validating patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert 'Patch operation has finished successfully.' in out.stdout
    assert out.stderr == "b''"

    generated_customtt = str(tmpdir) + \
        '/etc/apt/apt.conf.d/71_no_recommended.customtt.tt2'

    assert os.path.isfile(generated_customtt)
    with open(generated_customtt) as customtt:
        customtt_output = customtt.read()
    assert customtt_output == '''APT::Install-Recommends "1";\n'''

@pytest.mark.tt_24920
def test_patch_action_validate_patchtt_file(ngcpcfgcli, tmpdir):
    # ensure 'ngcpcfg patch' assert on corrupted patchtt file

    template_path = tmpdir.join('/etc')
    apt_path = template_path.join('/apt/apt.conf.d')
    os.makedirs(str(apt_path), exist_ok=True)

    apt_path.join('71_no_recommended.tt2').write('''
APT::Install-Recommends "0";
''')

    apt_path.join("71_no_recommended.patchtt.tt2").write('''
--- 71_no_recommended.tt2.orig  2017-12-08 13:31:49.763402557 +0100
+++ 71_no_recommended.tt2       2017-12-08 13:32:00.559382702 +0100
@@ -1,2 +1 @@
-
-bla-bla-bla
+bla-bla-bla-bla
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

    assert "Validating patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert "Error: The patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2' cannot be applied" in out.stderr
    assert "Error: Some operations above finished with an error for the patch(es)" in out.stderr
    assert 'Patch operation has finished successfully.' not in out.stdout

    # TODO: ensure no customtt.tt2 were generated

@pytest.mark.tt_24920
def test_patch_action_generate_requested_customtt_only(ngcpcfgcli, tmpdir):
    # ensure 'ngcpcfg patch .../some.patchtt.tt2' will build one requested patchtt only

    template_path = tmpdir.join('/etc')
    apt_path = template_path.join('/apt/apt.conf.d')
    os.makedirs(str(apt_path), exist_ok=True)

    apt_path.join('71_no_recommended.tt2').write('''
APT::Install-Recommends "0";
''')

    apt_path.join("71_no_recommended.patchtt.tt2").write('''
--- 71_no_recommended.tt2.orig  2017-12-08 13:31:49.763402557 +0100
+++ 71_no_recommended.tt2       2017-12-08 13:32:00.559382702 +0100
@@ -1,2 +1 @@
-
-APT::Install-Recommends "0";
+APT::Install-Recommends "1";
''')

    apt_path.join('72_another_file.tt2').write('''
# This is a dummy message you should not see
''')

    apt_path.join("72_another_file.patchtt.tt2").write('''
--- 71_no_recommended.tt2.orig  2017-12-08 13:31:49.763402557 +0100
+++ 71_no_recommended.tt2       2017-12-08 13:32:00.559382702 +0100
@@ -1,2 +1 @@
-
-# This is a dummy message you should not see
+# This is a dummy message you should not see on 'ngcpcfg build'
''')

    out = ngcpcfgcli("patch",
                     "/etc/apt/apt.conf.d/71_no_recommended.patchtt.tt2",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'NGCP_PORTFILE': '/tmp/ngcpcfg.port',
                         'OUTPUT_DIRECTORY': str(tmpdir),
                         'TEMPLATE_POOL_BASE': str(tmpdir),
                         'CONFIG_POOL': '/etc',
                         })

    assert "Validating patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert "Applying patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert "Successfully created '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.customtt.tt2'" in out.stdout
    assert '72_another_file.customtt.tt2' not in out.stdout
    assert 'Patch operation has finished successfully.' in out.stdout
    assert out.stderr == "b''"

    generated_customtt = str(tmpdir) + \
        '/etc/apt/apt.conf.d/71_no_recommended.customtt.tt2'

    assert os.path.isfile(generated_customtt)
    with open(generated_customtt) as customtt:
        customtt_output = customtt.read()
    assert customtt_output == '''APT::Install-Recommends "1";\n'''
    # TODO ensure file '/etc/apt/apt.conf.d/72_another_file.tt2' was not created

@pytest.mark.tt_24920
def test_patch_action_missing_patchtt_file(ngcpcfgcli, tmpdir):
    # ensure 'ngcpcfg patch' produce no errors if no patchtt file found

    template_path = tmpdir.join('/etc')
    apt_path = template_path.join('/apt/apt.conf.d')
    os.makedirs(str(apt_path), exist_ok=True)

    apt_path.join('71_no_recommended.tt2').write('''
APT::Install-Recommends "0";
''')

    out = ngcpcfgcli("patch",
                     "/etc/missing_patchtt_file.patchtt.tt2",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'NGCP_PORTFILE': '/tmp/ngcpcfg.port',
                         'OUTPUT_DIRECTORY': str(tmpdir),
                         'TEMPLATE_POOL_BASE': str(tmpdir),
                         'CONFIG_POOL': '/etc',
                         })

    assert 'No patchtt files found, nothing to patch.' in out.stdout
    assert out.stderr == "b''"

@pytest.mark.tt_24920
def test_patch_action_build_generate_and_overwrite_customtt_file(ngcpcfgcli, tmpdir):
    # We ensure here "ngcpcfg build" will:
    #   * find available patchtt file
    #   * validate available patchtt file
    #   * use available patchtt file
    #   * generate proper customtt file using tt2 + patchtt
    #   * overwrite old/available customtt file
    #   * build proper config using new customtt file

    template_path = tmpdir.join('/etc')
    apt_path = template_path.join('/apt/apt.conf.d')
    os.makedirs(str(apt_path), exist_ok=True)

    apt_path.join('71_no_recommended.tt2').write('''
APT::Install-Recommends "0";
''')

    apt_path.join('71_no_recommended.customtt.tt2').write('''
# generated via customtt without patch file
APT::Install-Recommends "2";
''')

    apt_path.join("71_no_recommended.patchtt.tt2").write('''
--- 71_no_recommended.tt2.orig   2018-01-10 15:24:06.951855880 +0100
+++ 71_no_recommended.tt2        2018-01-10 15:27:14.891237633 +0100
@@ -1 +1 @@
-APT::Install-Recommends "0";
+APT::Install-Recommends "1";

''')

    expected_output = '''
APT::Install-Recommends "1";
'''
    out = ngcpcfgcli("build", "--ignore-branch-check",
                     "/etc/apt/apt.conf.d/",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'NGCP_PORTFILE': '/tmp/ngcpcfg.port',
                         'OUTPUT_DIRECTORY': str(tmpdir) + "/output",
                         'TEMPLATE_POOL_BASE': str(tmpdir),
                         'CONFIG_POOL': '/etc',
                         })

    assert 'No patchtt files found, nothing to patch.' not in out.stdout
    assert "Validating patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert "Applying patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert "Successfully created '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.customtt.tt2'" in out.stdout
    assert 'Patch operation has finished successfully.' in out.stdout
    assert "Generating " + str(tmpdir) + "/output/" + str(tmpdir) + \
        "//etc/apt/apt.conf.d/71_no_recommended: OK" in out.stdout
    # disabled for the moment, see https://gerrit.mgm.sipwise.com/#/c/17739/4/t/test_ngcpcfg_patch.py@99
    #assert out.stderr == "b''"

    generated_customtt = str(template_path) + \
        '/apt/apt.conf.d/71_no_recommended.customtt.tt2'

    assert os.path.isfile(generated_customtt)
    with open(generated_customtt) as output_file:
        output = output_file.read()
    assert output == expected_output

    generated_config = str(tmpdir) + "/output" + str(tmpdir) + \
        '/etc/apt/apt.conf.d/71_no_recommended'

    assert os.path.isfile(generated_config)
    with open(generated_config) as output_file:
        output = output_file.read()
    assert output == expected_output

@pytest.mark.tt_24920
def test_patch_action_customtt_does_not_trigger_patch_file(ngcpcfgcli, tmpdir):
    # We ensure here new patch functionality on "ngcpcfg build"
    # will NOT affect current customtt logic if no patchtt file available

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

    assert 'No patchtt files found, nothing to patch.' in out.stdout
    assert 'Patch operation has finished successfully.' not in out.stdout
    assert 'Generating ' in out.stdout
    assert '/etc/apt/apt.conf.d/71_no_recommended: OK' in out.stdout
    assert 'Validating patch' not in out.stdout
    assert '71_no_recommended.customtt.tt2' not in out.stdout
    # disabled for the moment, see https://gerrit.mgm.sipwise.com/#/c/17739/4/t/test_ngcpcfg_patch.py@99
    #assert out.stderr == "b''"

    generated_config = str(tmpdir) + "/output" + str(tmpdir) + \
        '/etc/apt/apt.conf.d/71_no_recommended'

    assert os.path.isfile(generated_config)
    with open(generated_config) as output_file:
        output = output_file.read()
    assert output == expected_output
    # assert 0, out
