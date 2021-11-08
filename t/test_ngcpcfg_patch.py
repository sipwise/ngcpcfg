#!/usr/bin/env py.test-3

import os
import pytest
import re
import tempfile

###############################################################################
# tests for "ngcpcfg patch" (no options provides)
###############################################################################

@pytest.mark.tt_24920
def test_patch_action_no_args(ngcpcfgcli, tmpdir):
    out = ngcpcfgcli("patch")
    string = r"No patchtt files found, nothing to patch."
    assert string in out.stdout
    assert out.stderr == ""


@pytest.mark.tt_24920
def test_patch_action_help(ngcpcfgcli, tmpdir):
    # ensure 'ngcpcfg patch --help' works as expected

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
                     "--help",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'OUTPUT_DIRECTORY': str(tmpdir),
                         'TEMPLATE_POOL_BASE': str(tmpdir),
                         'CONFIG_POOL': '/etc',
                         'STATE_FILES_DIR': str(tmpdir) + '/var/lib/ngcpcfg/state/',
                         })

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout)
    print("stderr:")
    print(out.stderr)

    assert "'ngcpcfg patch' walks through all templates" in out.stdout
    assert "Validating patch" not in out.stdout
    assert 'Requested patchtt operation has finished successfully.' not in out.stdout
    assert out.stderr == ""


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
                         'OUTPUT_DIRECTORY': str(tmpdir),
                         'TEMPLATE_POOL_BASE': str(tmpdir),
                         'CONFIG_POOL': '/etc',
                         'STATE_FILES_DIR': str(tmpdir) + '/var/lib/ngcpcfg/state/',
                         })

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout)
    print("stderr:")
    print(out.stderr)

    assert "Validating patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert 'Requested patchtt operation has finished successfully.' in out.stdout
    assert out.stderr == ""

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
                         'OUTPUT_DIRECTORY': str(tmpdir),
                         'TEMPLATE_POOL_BASE': str(tmpdir),
                         'CONFIG_POOL': '/etc',
                         'STATE_FILES_DIR': str(tmpdir) + '/var/lib/ngcpcfg/state/',
                         })

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout)
    print("stderr:")
    print(out.stderr)

    assert "Validating patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert "Error: The patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2' cannot be applied" in out.stderr
    assert "Error: Some operations above finished with an error for the file(s)" in out.stderr
    assert 'Requested patchtt operation has finished successfully.' not in out.stdout

    # TODO: ensure no customtt.tt2 were generated


@pytest.mark.tt_24920
def test_patch_action_template_missing_for_patchtt(ngcpcfgcli, tmpdir):
    # ensure "ngcpcfg build" will be aborted if patchtt for missing template found

    template_path = tmpdir.join('/etc')
    apt_path = template_path.join('/apt/apt.conf.d')
    os.makedirs(str(apt_path), exist_ok=True)

    apt_path.join("71_no_recommended.patchtt.tt2").write('''
--- 71_no_recommended.tt2.orig  2017-12-08 13:31:49.763402557 +0100
+++ 71_no_recommended.tt2       2017-12-08 13:32:00.559382702 +0100
@@ -1,2 +1 @@
-
-the changes here
+doesn't matter as no tt2 file available
''')

    out = ngcpcfgcli("patch",
                     "/etc/apt/apt.conf.d/",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'OUTPUT_DIRECTORY': str(tmpdir),
                         'TEMPLATE_POOL_BASE': str(tmpdir),
                         'CONFIG_POOL': '/etc',
                         'STATE_FILES_DIR': str(tmpdir) + '/var/lib/ngcpcfg/state/',
                         })

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout)
    print("stderr:")
    print(out.stderr)

    assert "Validating patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert "Error: Missing template '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.tt2'" in out.stderr
    assert "Error: Some operations above finished with an error for the file(s)" in out.stderr
    assert 'Requested patchtt operation has finished successfully.' not in out.stdout


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
                         'OUTPUT_DIRECTORY': str(tmpdir),
                         'TEMPLATE_POOL_BASE': str(tmpdir),
                         'CONFIG_POOL': '/etc',
                         'STATE_FILES_DIR': str(tmpdir) + '/var/lib/ngcpcfg/state/',
                         })

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout)
    print("stderr:")
    print(out.stderr)

    assert "Validating patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert "Applying patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert "Successfully created '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.customtt.tt2'" in out.stdout
    assert '72_another_file.customtt.tt2' not in out.stdout
    assert 'Requested patchtt operation has finished successfully.' in out.stdout
    assert out.stderr == ""

    generated_customtt = str(tmpdir) + \
        '/etc/apt/apt.conf.d/71_no_recommended.customtt.tt2'

    assert os.path.isfile(generated_customtt)
    with open(generated_customtt) as customtt:
        customtt_output = customtt.read()
    assert customtt_output == '''APT::Install-Recommends "1";\n'''
    # TODO ensure file '/etc/apt/apt.conf.d/72_another_file.tt2' was not created


@pytest.mark.tt_24920
def test_patch_action_generate_requested_customtt_only_shortname(ngcpcfgcli, tmpdir):
    # ensure 'ngcpcfg patch .../some.patchtt.tt2' will build one
    # requested patchtt only using the short filename

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
                     "71_no_recommended.patchtt.tt2",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'OUTPUT_DIRECTORY': str(tmpdir),
                         'TEMPLATE_POOL_BASE': str(tmpdir),
                         'CONFIG_POOL': '/etc',
                         'STATE_FILES_DIR': str(tmpdir) + '/var/lib/ngcpcfg/state/',
                         })

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout)
    print("stderr:")
    print(out.stderr)

    assert "Validating patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert "Applying patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert "Successfully created '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.customtt.tt2'" in out.stdout
    assert '72_another_file.customtt.tt2' not in out.stdout
    assert 'Requested patchtt operation has finished successfully.' in out.stdout
    assert out.stderr == ""

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
                         'OUTPUT_DIRECTORY': str(tmpdir),
                         'TEMPLATE_POOL_BASE': str(tmpdir),
                         'CONFIG_POOL': '/etc',
                         'STATE_FILES_DIR': str(tmpdir) + '/var/lib/ngcpcfg/state/',
                         })

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout)
    print("stderr:")
    print(out.stderr)

    assert 'No patchtt files found, nothing to patch.' in out.stdout
    assert out.stderr == ""


@pytest.mark.tt_24920
def test_patch_action_build_generate_and_overwrite_customtt_file(ngcpcfgcli, tmpdir, gitrepo):
    # Ensure here "ngcpcfg build" will:
    #   * find available patchtt file
    #   * validate available patchtt file (necessary only)
    #   * use available patchtt file
    #   * care about patchtt.tt2.sp1 file
    #   * generate proper customtt files using tt2 + patchtt
    #   * overwrite old/available customtt files
    #   * build proper config using new customtt files

    template_path = tmpdir.join('/etc')
    apt_path = template_path.join('/apt/apt.conf.d')
    dummy_path = template_path.join('/dummy')
    os.makedirs(str(apt_path), exist_ok=True)
    os.makedirs(str(dummy_path), exist_ok=True)

    apt_path.join('71_no_recommended.tt2').write('''
APT::Install-Recommends "0";
''')

    apt_path.join('71_no_recommended.customtt.tt2').write('''
# generated via customtt without patch file
APT::Install-Recommends "2";
''')

    expected_output = '''
APT::Install-Recommends "1";
'''

    apt_path.join("71_no_recommended.patchtt.tt2").write('''
--- 71_no_recommended.tt2.orig   2018-01-10 15:24:06.951855880 +0100
+++ 71_no_recommended.tt2        2018-01-10 15:27:14.891237633 +0100
@@ -1 +1 @@
-APT::Install-Recommends "0";
+APT::Install-Recommends "1";

''')

    apt_path.join('71_no_recommended.customtt.tt2.sp1').write('''
# generated via customtt.sp1 without patch file
APT::Install-Recommends "3";
''')

    apt_path.join("71_no_recommended.patchtt.tt2.sp1").write('''
@@ -1 +1 @@
-APT::Install-Recommends "0";
+APT::Install-Recommends "3";

''')

    expected_output_sp1 = '''
APT::Install-Recommends "1";
'''

    dummy_path.join('dummy.tt2').write('''
dome dummy template message
''')

    dummy_path.join('dummy.customtt.tt2').write('''
dome dummy customtt message
''')

    dummy_path.join("dummy.patchtt.tt2").write('''
@@ -1 +1 @@
-dome dummy template message
+dome dummy customtt message
''')
    src = "basic-ngcp-config.tar.gz"
    with gitrepo.from_archive(src):
        cfg_dir = os.path.join(gitrepo.localpath, "ngcp-config")
        out = ngcpcfgcli(
            "build",
            "--ignore-branch-check",
            "/etc/apt/apt.conf.d/",
            env={
                "NGCPCTL_MAIN": cfg_dir,
                # we just need a clean git repo
                "NGCPCTL_BASE": cfg_dir,
                'NGCP_BASE_TT2': os.getcwd(),
                'OUTPUT_DIRECTORY': str(tmpdir) + "/output",
                'TEMPLATE_POOL_BASE': str(tmpdir),
                'CONFIG_POOL': '/etc',
                'STATE_FILES_DIR': str(tmpdir) + '/var/lib/ngcpcfg/state/',
            }
        )

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout)
    print("stderr:")
    print(out.stderr)

    assert 'No patchtt files found, nothing to patch.' not in out.stdout
    assert 'dummy' not in out.stdout
    assert "Validating patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert "Validating patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2.sp1'" in out.stdout
    assert "Applying patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert "Successfully created '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.customtt.tt2'" in out.stdout
    assert "Applying patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2.sp1'" in out.stdout
    assert "Successfully created '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.customtt.tt2.sp1'" in out.stdout
    assert 'Requested patchtt operation has finished successfully.' in out.stdout
    assert "Generating " + str(tmpdir) + "/output" + str(tmpdir) + \
        "/etc/apt/apt.conf.d/71_no_recommended: OK" in out.stdout
    assert out.stderr == ""

    generated_customtt = str(template_path) + \
        '/apt/apt.conf.d/71_no_recommended.customtt.tt2'

    assert os.path.isfile(generated_customtt)
    with open(generated_customtt) as output_file:
        output = output_file.read()
    assert output == expected_output

    generated_customtt_sp1 = str(template_path) + \
        '/apt/apt.conf.d/71_no_recommended.customtt.tt2.sp1'

    assert os.path.isfile(generated_customtt)
    with open(generated_customtt) as output_file:
        output = output_file.read()
    assert output == expected_output_sp1

    generated_config = str(tmpdir) + "/output" + str(tmpdir) + \
        '/etc/apt/apt.conf.d/71_no_recommended'

    assert os.path.isfile(generated_config)
    with open(generated_config) as output_file:
        output = output_file.read()
    assert output == expected_output


@pytest.mark.tt_24920
def test_patch_action_build_generate_all_file(ngcpcfgcli, tmpdir, gitrepo):
    # the same as test 'test_patch_action_build_generate_and_overwrite_customtt_file'
    # while build all available files

    template_path = tmpdir.join('/etc')
    apt_path = template_path.join('/apt/apt.conf.d')
    dummy_path = template_path.join('/dummy')
    os.makedirs(str(apt_path), exist_ok=True)
    os.makedirs(str(dummy_path), exist_ok=True)

    apt_path.join('71_no_recommended.tt2').write('''
APT::Install-Recommends "0";
''')

    apt_path.join('71_no_recommended.customtt.tt2').write('''
# generated via customtt without patch file
APT::Install-Recommends "2";
''')

    expected_output = '''
APT::Install-Recommends "1";
'''

    apt_path.join("71_no_recommended.patchtt.tt2").write('''
--- 71_no_recommended.tt2.orig   2018-01-10 15:24:06.951855880 +0100
+++ 71_no_recommended.tt2        2018-01-10 15:27:14.891237633 +0100
@@ -1 +1 @@
-APT::Install-Recommends "0";
+APT::Install-Recommends "1";

''')

    apt_path.join('71_no_recommended.customtt.tt2.sp1').write('''
# generated via customtt.sp1 without patch file
APT::Install-Recommends "3";
''')

    apt_path.join("71_no_recommended.patchtt.tt2.sp1").write('''
@@ -1 +1 @@
-APT::Install-Recommends "0";
+APT::Install-Recommends "3";

''')

    expected_output_sp1 = '''
APT::Install-Recommends "1";
'''

    dummy_path.join('dummy.tt2').write('''
dome dummy template message
''')

    dummy_path.join('dummy.customtt.tt2').write('''
dome dummy customtt message
''')

    dummy_path.join("dummy.patchtt.tt2").write('''
@@ -1 +1 @@
-dome dummy template message
+dome dummy customtt message
''')
    src = "basic-ngcp-config.tar.gz"
    with gitrepo.from_archive(src):
        cfg_dir = os.path.join(gitrepo.localpath, "ngcp-config")
        out = ngcpcfgcli(
            "build",
            "--ignore-branch-check",
            env={
                "NGCPCTL_MAIN": cfg_dir,
                # we just need a clean git repo
                "NGCPCTL_BASE": cfg_dir,
                'NGCP_BASE_TT2': os.getcwd(),
                'OUTPUT_DIRECTORY': str(tmpdir) + "/output",
                'TEMPLATE_POOL_BASE': str(tmpdir),
                'CONFIG_POOL': '/etc',
                'STATE_FILES_DIR': str(tmpdir) + '/var/lib/ngcpcfg/state/',
            }
        )

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout)
    print("stderr:")
    print(out.stderr)

    assert 'No patchtt files found, nothing to patch.' not in out.stdout
    assert "Validating patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert "Validating patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2.sp1'" in out.stdout
    assert "Validating patch '" + str(template_path) + \
        "/dummy/dummy.patchtt.tt2'" in out.stdout
    assert "Applying patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert "Successfully created '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.customtt.tt2'" in out.stdout
    assert "Applying patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2.sp1'" in out.stdout
    assert "Successfully created '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.customtt.tt2.sp1'" in out.stdout
    assert "Applying patch '" + str(template_path) + \
        "/dummy/dummy.patchtt.tt2'" in out.stdout
    assert "Successfully created '" + str(template_path) + \
        "/dummy/dummy.customtt.tt2'" in out.stdout
    assert 'Requested patchtt operation has finished successfully.' in out.stdout
    assert "Generating " + str(tmpdir) + "/output" + str(tmpdir) + \
        "/etc/apt/apt.conf.d/71_no_recommended: OK" in out.stdout
    assert out.stderr == ""

    generated_customtt = str(template_path) + \
        '/apt/apt.conf.d/71_no_recommended.customtt.tt2'

    assert os.path.isfile(generated_customtt)
    with open(generated_customtt) as output_file:
        output = output_file.read()
    assert output == expected_output

    generated_customtt_sp1 = str(template_path) + \
        '/apt/apt.conf.d/71_no_recommended.customtt.tt2.sp1'

    assert os.path.isfile(generated_customtt)
    with open(generated_customtt) as output_file:
        output = output_file.read()
    assert output == expected_output_sp1

    generated_config = str(tmpdir) + "/output" + str(tmpdir) + \
        '/etc/apt/apt.conf.d/71_no_recommended'

    assert os.path.isfile(generated_config)
    with open(generated_config) as output_file:
        output = output_file.read()
    assert output == expected_output


@pytest.mark.tt_24920
def test_patch_action_customtt_does_not_trigger_patch_file(ngcpcfgcli, tmpdir, gitrepo):
    # ensure here new patch functionality on "ngcpcfg build"
    # will NOT affect current customtt logic if no patchtt file available

    template_path = tmpdir.join('/etc')
    apt_path = template_path.join('/apt/apt.conf.d')
    os.makedirs(str(apt_path), exist_ok=True)

    apt_path.join('71_no_recommended.tt2').write('''
APT::Install-Recommends "0";
''')

    expected_output = '''
# generated via customtt without patch file
APT::Install-Recommends "1";
'''

    customtt = apt_path.join("71_no_recommended.customtt.tt2")
    customtt.write(expected_output)

    src = "basic-ngcp-config.tar.gz"
    with gitrepo.from_archive(src):
        cfg_dir = os.path.join(gitrepo.localpath, "ngcp-config")
        out = ngcpcfgcli(
            "build",
            "--ignore-branch-check",
            "/etc/apt/apt.conf.d/",
            env={
                "NGCPCTL_MAIN": cfg_dir,
                # we just need a clean git repo
                "NGCPCTL_BASE": cfg_dir,
                'NGCP_BASE_TT2': os.getcwd(),
                'OUTPUT_DIRECTORY': str(tmpdir) + "/output",
                'TEMPLATE_POOL_BASE': str(tmpdir),
                'CONFIG_POOL': '/etc',
                'STATE_FILES_DIR': str(tmpdir) + '/var/lib/ngcpcfg/state/',
            }
        )

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout)
    print("stderr:")
    print(out.stderr)

    assert 'No patchtt files found, nothing to patch.' in out.stdout
    assert 'Requested patchtt operation has finished successfully.' not in out.stdout
    assert 'Generating ' in out.stdout
    assert '/etc/apt/apt.conf.d/71_no_recommended: OK' in out.stdout
    assert 'Validating patch' not in out.stdout
    assert '71_no_recommended.customtt.tt2' not in out.stdout
    assert out.stderr == ""

    generated_config = str(tmpdir) + "/output" + str(tmpdir) + \
        '/etc/apt/apt.conf.d/71_no_recommended'

    assert os.path.isfile(generated_config)
    with open(generated_config) as output_file:
        output = output_file.read()
    assert output == expected_output


@pytest.mark.tt_24920
def test_patch_action_build_patch_cannot_apply(ngcpcfgcli, tmpdir):
    # ensure 'ngcpcfg build' will be aborted if patch cannot be applied

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

    out = ngcpcfgcli("build", "--ignore-branch-check",
                     "/etc/apt/apt.conf.d/",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'OUTPUT_DIRECTORY': str(tmpdir) + "/output",
                         'TEMPLATE_POOL_BASE': str(tmpdir),
                         'CONFIG_POOL': '/etc',
                         'STATE_FILES_DIR': str(tmpdir) + '/var/lib/ngcpcfg/state/',
                         })

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout)
    print("stderr:")
    print(out.stderr)

    assert "Validating patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert "Error: The patch '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2' cannot be applied" in out.stderr
    assert "Error: Some operations above finished with an error for the file(s)" in out.stderr
    assert 'Requested patchtt operation has finished successfully.' not in out.stdout
    assert 'Generating ' not in out.stdout
    assert '/etc/apt/apt.conf.d/71_no_recommended: OK' not in out.stdout


###############################################################################
# tests for "ngcpcfg patch --from-customtt"
###############################################################################


@pytest.mark.tt_24920
def test_patch_action_from_customtt_files(ngcpcfgcli, tmpdir):
    # Ensure here "ngcpcfg patch --from-customtt" will:
    #   * find all available customtt file
    #   * create all necessary patchtt files

    template_path = tmpdir.join('/etc')
    apt_path = template_path.join('/apt/apt.conf.d')
    os.makedirs(str(apt_path), exist_ok=True)

    apt_path.join('71_no_recommended.tt2').write('''
# some comment
APT::Install-Recommends "0";
''')

    apt_path.join('71_no_recommended.customtt.tt2').write('''
# some comment
APT::Install-Recommends "2";
''')

    template_path.join('expected_patch.diff').write('''@@ -1,3 +1,3 @@
 
 # some comment
-APT::Install-Recommends "0";
+APT::Install-Recommends "2";
''')

    out = ngcpcfgcli("patch", "--from-customtt",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'OUTPUT_DIRECTORY': str(tmpdir) + "/output",
                         'TEMPLATE_POOL_BASE': str(tmpdir),
                         'CONFIG_POOL': '/etc',
                         'STATE_FILES_DIR': str(tmpdir) + '/var/lib/ngcpcfg/state/',
                         })

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout)
    print("stderr:")
    print(out.stderr)

    assert 'No patchtt files found, nothing to patch.' not in out.stdout
    assert "Validating customtt '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.customtt.tt2'" in out.stdout
    assert "Creating patchtt file '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert 'Requested customtt operation has finished successfully.' in out.stdout
    assert out.stderr == ""

    generated_patchtt = str(template_path) + \
        '/apt/apt.conf.d/71_no_recommended.patchtt.tt2'
    expected_patchtt = str(template_path) + \
        '/expected_patch.diff'

    assert os.path.isfile(generated_patchtt)
    assert os.path.isfile(expected_patchtt)
    with open(generated_patchtt) as output_file:
        output = output_file.read()
    with open(expected_patchtt) as expected_file:
        expected = expected_file.read()
    assert output == expected


@pytest.mark.tt_24920
def test_patch_action_from_customtt_missing_file_argument(ngcpcfgcli, tmpdir):
    # ensure "ngcpcfg patch --from-customtt missing.customtt.tt2" will be handled properly if
    # no some.customtt.tt2 file are available

    out = ngcpcfgcli("patch",
                     "--from-customtt",
                     "missing.customtt.tt2",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'OUTPUT_DIRECTORY': str(tmpdir),
                         'TEMPLATE_POOL_BASE': str(tmpdir),
                         'CONFIG_POOL': '/etc',
                         'STATE_FILES_DIR': str(tmpdir) + '/var/lib/ngcpcfg/state/',
                         })

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout)
    print("stderr:")
    print(out.stderr)

    assert 'No customtt files found, nothing to patch.' in out.stdout
    assert "Creating patchtt file '" not in out.stdout
    # disabled for the moment, see https://gerrit.mgm.sipwise.com/#/c/17739/4/t/test_ngcpcfg_patch.py@99
    #assert out.stderr == "b''"


@pytest.mark.tt_24920
def test_patch_action_from_customtt_filename_only(ngcpcfgcli, tmpdir):
    # ensure "ngcpcfg patch --from-customtt valid.customtt.tt2" will be handled properly if
    # no filename only valid.customtt.tt2 has been passed instead of full path

    template_path = tmpdir.join('/etc')
    apt_path = template_path.join('/apt/apt.conf.d')
    os.makedirs(str(apt_path), exist_ok=True)

    apt_path.join('71_no_recommended.tt2').write('''
# some comment
APT::Install-Recommends "0";
''')

    apt_path.join('71_no_recommended.customtt.tt2').write('''
# some comment
APT::Install-Recommends "2";
''')

    template_path.join('expected_patch.diff').write('''@@ -1,3 +1,3 @@
 
 # some comment
-APT::Install-Recommends "0";
+APT::Install-Recommends "2";
''')

    out = ngcpcfgcli("patch",
                     "--from-customtt",
                     "71_no_recommended.customtt.tt2",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'OUTPUT_DIRECTORY': str(tmpdir),
                         'TEMPLATE_POOL_BASE': str(tmpdir),
                         'CONFIG_POOL': '/etc',
                         })

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout)
    print("stderr:")
    print(out.stderr)

    assert 'No patchtt files found, nothing to patch.' not in out.stdout
    assert "Validating customtt '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.customtt.tt2'" in out.stdout
    assert "Creating patchtt file '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.patchtt.tt2'" in out.stdout
    assert 'Requested customtt operation has finished successfully.' in out.stdout
    assert out.stderr == ""

    generated_patchtt = str(template_path) + \
        '/apt/apt.conf.d/71_no_recommended.patchtt.tt2'
    expected_patchtt = str(template_path) + \
        '/expected_patch.diff'

    assert os.path.isfile(generated_patchtt)
    assert os.path.isfile(expected_patchtt)
    with open(generated_patchtt) as output_file:
        output = output_file.read()
    with open(expected_patchtt) as expected_file:
        expected = expected_file.read()
    assert output == expected


@pytest.mark.tt_24920
def test_patch_action_from_customtt_missing_templates(ngcpcfgcli, tmpdir):
    # ensure "ngcpcfg patch --from-customtt" will be aborted if template is missing for customtt

    template_path = tmpdir.join('/etc')
    apt_path = template_path.join('/apt/apt.conf.d')
    os.makedirs(str(apt_path), exist_ok=True)

    apt_path.join("71_no_recommended.customtt.tt2").write('''
the content here doesn't matter as no tt2 file available
''')

    out = ngcpcfgcli("patch",
                     "--from-customtt",
                     env={
                         'NGCP_BASE_TT2': os.getcwd(),
                         'OUTPUT_DIRECTORY': str(tmpdir),
                         'TEMPLATE_POOL_BASE': str(tmpdir),
                         'CONFIG_POOL': '/etc',
                         'STATE_FILES_DIR': str(tmpdir) + '/var/lib/ngcpcfg/state/',
                         })

    # debug, only printed in logs in case of error
    print("stdout:")
    print(out.stdout)
    print("stderr:")
    print(out.stderr)

    assert "Validating customtt '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.customtt.tt2'" in out.stdout
    assert "Error: Missing template for customtt '" + str(template_path) + \
        "/apt/apt.conf.d/71_no_recommended.customtt.tt2'" in out.stderr
    assert "Error: Some operations above finished with an error for the file(s)" in out.stderr
    assert 'Requested patchtt operation has finished successfully.' not in out.stdout
