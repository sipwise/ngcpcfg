#!/usr/bin/env py.test-3
import shutil
from pathlib import Path

import pytest
from fixtures.fs import check_output

###############################################################################
# tests for "ngcpcfg patch" (no options provides)
###############################################################################


@pytest.mark.tt_24920
def test_patch_action_no_args(ngcpcfgcli):
    out = ngcpcfgcli("patch")
    string = r"No patchtt files found, nothing to patch."
    assert string in out.stdout
    assert out.returncode == 0


# @pytest.mark.tt_24920
def test_patch_action_help(ngcpcfg, ngcpcfgcli, tmpdir):
    # ensure 'ngcpcfg patch --help' works as expected
    env, cfg = ngcpcfg()
    template_pool = Path(cfg["TEMPLATE_POOL_BASE"]).joinpath("etc")
    shutil.rmtree(template_pool)
    apt_path = template_pool.joinpath("apt/apt.conf.d")
    apt_path.mkdir(parents=True, exist_ok=True)

    apt_path.joinpath("71_no_recommended.tt2").write_text(
        """
APT::Install-Recommends "0";
"""
    )

    apt_path.joinpath("71_no_recommended.patchtt.tt2").write_text(
        """
--- 71_no_recommended.tt2.orig  2017-12-08 13:31:49.763402557 +0100
+++ 71_no_recommended.tt2       2017-12-08 13:32:00.559382702 +0100
@@ -1,2 +1 @@
-
-bla-bla-bla
+bla-bla-bla-bla
"""
    )

    out = ngcpcfgcli(
        "patch",
        "--help",
        env=env,
    )

    assert "'ngcpcfg patch' walks through all templates" in out.stdout
    assert "Validating patch" not in out.stdout
    assert "Requested patchtt operation has finished successfully." not in out.stdout
    assert out.returncode == 0


@pytest.mark.tt_24920
def test_patch_action_generate_customtt_via_patchtt_file(ngcpcfg, ngcpcfgcli):
    # ensure 'ngcpcfg patch' works in the most simple case

    env, cfg = ngcpcfg()
    template_pool = Path(cfg["TEMPLATE_POOL_BASE"]).joinpath("etc")
    shutil.rmtree(template_pool)
    apt_path = template_pool.joinpath("apt/apt.conf.d")
    apt_path.mkdir(parents=True, exist_ok=True)

    apt_path.joinpath("71_no_recommended.tt2").write_text(
        """
APT::Install-Recommends "0";
"""
    )

    apt_path.joinpath("71_no_recommended.patchtt.tt2").write_text(
        """
--- 71_no_recommended.tt2.orig  2017-12-08 13:31:49.763402557 +0100
+++ 71_no_recommended.tt2       2017-12-08 13:32:00.559382702 +0100
@@ -1,2 +1 @@
-
-APT::Install-Recommends "0";
+APT::Install-Recommends "1";
"""
    )

    out = ngcpcfgcli(
        "patch",
        "/etc/apt/apt.conf.d/",
        env=env,
    )

    assert (
        "Validating patch '" + str(apt_path) + "/71_no_recommended.patchtt.tt2'"
        in out.stdout
    )
    assert "Requested patchtt operation has finished successfully." in out.stdout
    assert out.returncode == 0

    generated_customtt = apt_path.joinpath("71_no_recommended.customtt.tt2")
    assert generated_customtt.read_text() == """APT::Install-Recommends "1";\n"""


@pytest.mark.tt_24920
def test_patch_action_validate_patchtt_file(ngcpcfg, ngcpcfgcli):
    # ensure 'ngcpcfg patch' assert on corrupted patchtt file

    env, cfg = ngcpcfg()
    template_pool = Path(cfg["TEMPLATE_POOL_BASE"]).joinpath("etc")
    shutil.rmtree(template_pool)
    apt_path = template_pool.joinpath("apt/apt.conf.d")
    apt_path.mkdir(parents=True, exist_ok=True)

    apt_path.joinpath("71_no_recommended.tt2").write_text(
        """
APT::Install-Recommends "0";
"""
    )

    apt_path.joinpath("71_no_recommended.patchtt.tt2").write_text(
        """
--- 71_no_recommended.tt2.orig  2017-12-08 13:31:49.763402557 +0100
+++ 71_no_recommended.tt2       2017-12-08 13:32:00.559382702 +0100
@@ -1,2 +1 @@
-
-bla-bla-bla
+bla-bla-bla-bla
"""
    )

    out = ngcpcfgcli(
        "patch",
        "/etc/apt/apt.conf.d/",
        env=env,
    )

    assert (
        "Validating patch '" + str(apt_path) + "/71_no_recommended.patchtt.tt2'"
        in out.stdout
    )
    assert (
        "Error: The patch '"
        + str(apt_path)
        + "/71_no_recommended.patchtt.tt2' cannot be applied"
        in out.stderr
    )
    assert (
        "Error: Some operations above finished with an error for the file(s)"
        in out.stderr
    )
    assert "Requested patchtt operation has finished successfully." not in out.stdout

    generated_customtt = apt_path.joinpath("71_no_recommended.customtt.tt2")
    assert not generated_customtt.exists()
    assert out.returncode != 0


@pytest.mark.tt_24920
def test_patch_action_template_missing_for_patchtt(ngcpcfg, ngcpcfgcli):
    # ensure "ngcpcfg build" will be aborted if patchtt for missing template found

    env, cfg = ngcpcfg()
    template_pool = Path(cfg["TEMPLATE_POOL_BASE"]).joinpath("etc")
    shutil.rmtree(template_pool)
    apt_path = template_pool.joinpath("apt/apt.conf.d")
    apt_path.mkdir(parents=True, exist_ok=True)

    apt_path.joinpath("71_no_recommended.patchtt.tt2").write_text(
        """
--- 71_no_recommended.tt2.orig  2017-12-08 13:31:49.763402557 +0100
+++ 71_no_recommended.tt2       2017-12-08 13:32:00.559382702 +0100
@@ -1,2 +1 @@
-
-the changes here
+doesn't matter as no tt2 file available
"""
    )

    out = ngcpcfgcli(
        "patch",
        "/etc/apt/apt.conf.d/",
        env=env,
    )

    assert (
        "Validating patch '" + str(apt_path) + "/71_no_recommended.patchtt.tt2'"
        in out.stdout
    )
    assert (
        "Error: Missing template '" + str(apt_path) + "/71_no_recommended.tt2'"
        in out.stderr
    )
    assert (
        "Error: Some operations above finished with an error for the file(s)"
        in out.stderr
    )
    assert "Requested patchtt operation has finished successfully." not in out.stdout
    assert out.returncode != 0


@pytest.mark.tt_24920
def test_patch_action_generate_requested_customtt_only(ngcpcfg, ngcpcfgcli):
    # ensure 'ngcpcfg patch .../some.patchtt.tt2' will build one requested patchtt only

    env, cfg = ngcpcfg()
    template_pool = Path(cfg["TEMPLATE_POOL_BASE"]).joinpath("etc")
    shutil.rmtree(template_pool)
    apt_path = template_pool.joinpath("apt/apt.conf.d")
    apt_path.mkdir(parents=True, exist_ok=True)

    apt_path.joinpath("71_no_recommended.tt2").write_text(
        """
APT::Install-Recommends "0";
"""
    )

    apt_path.joinpath("71_no_recommended.patchtt.tt2").write_text(
        """
--- 71_no_recommended.tt2.orig  2017-12-08 13:31:49.763402557 +0100
+++ 71_no_recommended.tt2       2017-12-08 13:32:00.559382702 +0100
@@ -1,2 +1 @@
-
-APT::Install-Recommends "0";
+APT::Install-Recommends "1";
"""
    )
    apt_path.joinpath("72_another_file.tt2").write_text(
        """
# This is a dummy message you should not see
"""
    )

    apt_path.joinpath("72_another_file.patchtt.tt2").write_text(
        """
--- 71_no_recommended.tt2.orig  2017-12-08 13:31:49.763402557 +0100
+++ 71_no_recommended.tt2       2017-12-08 13:32:00.559382702 +0100
@@ -1,2 +1 @@
-
-# This is a dummy message you should not see
+# This is a dummy message you should not see on 'ngcpcfg build'
"""
    )

    out = ngcpcfgcli(
        "patch",
        "/etc/apt/apt.conf.d/71_no_recommended.patchtt.tt2",
        env=env,
    )

    assert (
        "Validating patch '" + str(apt_path) + "/71_no_recommended.patchtt.tt2'"
        in out.stdout
    )
    assert (
        "Applying patch '" + str(apt_path) + "/71_no_recommended.patchtt.tt2'"
        in out.stdout
    )
    assert (
        "Successfully created '" + str(apt_path) + "/71_no_recommended.customtt.tt2'"
        in out.stdout
    )
    assert "72_another_file.customtt.tt2" not in out.stdout
    assert "Requested patchtt operation has finished successfully." in out.stdout
    assert out.returncode == 0

    generated_customtt = apt_path.joinpath("71_no_recommended.customtt.tt2")
    generated_customtt.read_text() == """APT::Install-Recommends "1";\n"""
    assert not apt_path.joinpath("72_another_file.customtt.tt2").exists()


@pytest.mark.tt_24920
def test_patch_action_generate_requested_customtt_only_shortname(ngcpcfg, ngcpcfgcli):
    # ensure 'ngcpcfg patch .../some.patchtt.tt2' will build one
    # requested patchtt only using the short filename

    env, cfg = ngcpcfg()
    template_pool = Path(cfg["TEMPLATE_POOL_BASE"]).joinpath("etc")
    shutil.rmtree(template_pool)
    apt_path = template_pool.joinpath("apt/apt.conf.d")
    apt_path.mkdir(parents=True, exist_ok=True)

    apt_path.joinpath("71_no_recommended.tt2").write_text(
        """
APT::Install-Recommends "0";
"""
    )

    apt_path.joinpath("71_no_recommended.patchtt.tt2").write_text(
        """
--- 71_no_recommended.tt2.orig  2017-12-08 13:31:49.763402557 +0100
+++ 71_no_recommended.tt2       2017-12-08 13:32:00.559382702 +0100
@@ -1,2 +1 @@
-
-APT::Install-Recommends "0";
+APT::Install-Recommends "1";
"""
    )

    apt_path.joinpath("72_another_file.tt2").write_text(
        """
# This is a dummy message you should not see
"""
    )

    apt_path.joinpath("72_another_file.patchtt.tt2").write_text(
        """
--- 71_no_recommended.tt2.orig  2017-12-08 13:31:49.763402557 +0100
+++ 71_no_recommended.tt2       2017-12-08 13:32:00.559382702 +0100
@@ -1,2 +1 @@
-
-# This is a dummy message you should not see
+# This is a dummy message you should not see on 'ngcpcfg build'
"""
    )

    out = ngcpcfgcli(
        "patch",
        "71_no_recommended.patchtt.tt2",
        env=env,
    )

    assert (
        "Validating patch '" + str(apt_path) + "/71_no_recommended.patchtt.tt2'"
        in out.stdout
    )
    assert (
        "Applying patch '" + str(apt_path) + "/71_no_recommended.patchtt.tt2'"
        in out.stdout
    )
    assert (
        "Successfully created '" + str(apt_path) + "/71_no_recommended.customtt.tt2'"
        in out.stdout
    )
    assert "72_another_file.customtt.tt2" not in out.stdout
    assert "Requested patchtt operation has finished successfully." in out.stdout
    assert out.returncode == 0

    generated_customtt = apt_path.joinpath("71_no_recommended.customtt.tt2")
    generated_customtt.read_text() == """APT::Install-Recommends "1";\n"""
    assert not apt_path.joinpath("72_another_file.customtt.tt2").exists()


@pytest.mark.tt_24920
def test_patch_action_missing_patchtt_file(ngcpcfg, ngcpcfgcli):
    # ensure 'ngcpcfg patch' produce no errors if no patchtt file found

    env, cfg = ngcpcfg()
    template_pool = Path(cfg["TEMPLATE_POOL_BASE"]).joinpath("etc")
    shutil.rmtree(template_pool)
    apt_path = template_pool.joinpath("apt/apt.conf.d")
    apt_path.mkdir(parents=True, exist_ok=True)

    apt_path.joinpath("71_no_recommended.tt2").write_text(
        """
APT::Install-Recommends "0";
"""
    )

    out = ngcpcfgcli(
        "patch",
        "/etc/missing_patchtt_file.patchtt.tt2",
        env=env,
    )

    assert "No patchtt files found, nothing to patch." in out.stdout
    assert out.returncode == 0


@pytest.mark.tt_24920
def test_patch_action_build_generate_and_overwrite_customtt_file(ngcpcfg, ngcpcfgcli):
    # Ensure here "ngcpcfg build" will:
    #   * find available patchtt file
    #   * validate available patchtt file (necessary only)
    #   * use available patchtt file
    #   * care about patchtt.tt2.sp1 file
    #   * generate proper customtt files using tt2 + patchtt
    #   * overwrite old/available customtt files
    #   * build proper config using new customtt files

    env, cfg = ngcpcfg(
        env={
            "NGCPCFG": "fixtures/ngcpcfg_pro.cfg",
        },
    )
    template_pool = Path(cfg["TEMPLATE_POOL_BASE"]).joinpath("etc")
    shutil.rmtree(template_pool)
    apt_path = template_pool.joinpath("apt/apt.conf.d")
    apt_path.mkdir(parents=True, exist_ok=True)
    dummy_path = template_pool.joinpath("dummy")
    dummy_path.mkdir()

    apt_path.joinpath("71_no_recommended.tt2").write_text(
        """
APT::Install-Recommends "0";
"""
    )

    apt_path.joinpath("71_no_recommended.customtt.tt2").write_text(
        """
# generated via customtt without patch file
APT::Install-Recommends "2";
"""
    )

    expected_output = """
APT::Install-Recommends "1";
"""

    apt_path.joinpath("71_no_recommended.patchtt.tt2").write_text(
        """
--- 71_no_recommended.tt2.orig   2018-01-10 15:24:06.951855880 +0100
+++ 71_no_recommended.tt2        2018-01-10 15:27:14.891237633 +0100
@@ -1 +1 @@
-APT::Install-Recommends "0";
+APT::Install-Recommends "1";

"""
    )

    apt_path.joinpath("71_no_recommended.customtt.tt2.sp1").write_text(
        """
# generated via customtt.sp1 without patch file
APT::Install-Recommends "3";
"""
    )

    apt_path.joinpath("71_no_recommended.patchtt.tt2.sp1").write_text(
        """
@@ -1 +1 @@
-APT::Install-Recommends "0";
+APT::Install-Recommends "3";

"""
    )

    expected_output_sp1 = """
APT::Install-Recommends "1";
"""

    dummy_path.joinpath("dummy.tt2").write_text(
        """
dome dummy template message
"""
    )

    dummy_path.joinpath("dummy.customtt.tt2").write_text(
        """
dome dummy customtt message
"""
    )

    dummy_path.joinpath("dummy.patchtt.tt2").write_text(
        """
@@ -1 +1 @@
-dome dummy template message
+dome dummy customtt message
"""
    )
    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/apt/apt.conf.d/",
        env=env,
    )

    assert "No patchtt files found, nothing to patch." not in out.stdout
    assert "dummy" not in out.stdout
    assert (
        "Validating patch '" + str(apt_path) + "/71_no_recommended.patchtt.tt2'"
        in out.stdout
    )
    assert (
        "Validating patch '" + str(apt_path) + "/71_no_recommended.patchtt.tt2.sp1'"
        in out.stdout
    )
    assert (
        "Applying patch '" + str(apt_path) + "/71_no_recommended.patchtt.tt2'"
        in out.stdout
    )
    assert (
        "Successfully created '" + str(apt_path) + "/71_no_recommended.customtt.tt2'"
        in out.stdout
    )
    assert (
        "Applying patch '" + str(apt_path) + "/71_no_recommended.patchtt.tt2.sp1'"
        in out.stdout
    )
    assert (
        "Successfully created '"
        + str(apt_path)
        + "/71_no_recommended.customtt.tt2.sp1'"
        in out.stdout
    )
    assert "Requested patchtt operation has finished successfully." in out.stdout
    assert (
        "Generating "
        + str(out.env["OUTPUT_DIRECTORY"])
        + "/etc/apt/apt.conf.d/71_no_recommended: OK"
        in out.stdout
    )
    assert out.returncode == 0

    generated_customtt = apt_path.joinpath("71_no_recommended.customtt.tt2")
    generated_customtt.read_text() == expected_output

    generated_customtt = apt_path.joinpath("71_no_recommended.customtt.tt2.sp1")
    generated_customtt.read_text() == expected_output_sp1

    generated_config = out.env["OUTPUT_DIRECTORY"].joinpath(
        "etc/apt/apt.conf.d/71_no_recommended"
    )
    assert generated_config.read_text() == expected_output


@pytest.mark.tt_24920
def test_patch_action_build_generate_all_file(ngcpcfg, ngcpcfgcli):
    # the same as test 'test_patch_action_build_generate_and_overwrite_customtt_file'
    # while build all available files

    env, cfg = ngcpcfg(
        env={
            "NGCPCFG": "fixtures/ngcpcfg_pro.cfg",
        },
    )
    template_pool = Path(cfg["TEMPLATE_POOL_BASE"]).joinpath("etc")
    shutil.rmtree(template_pool)
    apt_path = template_pool.joinpath("apt/apt.conf.d")
    apt_path.mkdir(parents=True, exist_ok=True)
    dummy_path = template_pool.joinpath("dummy")
    dummy_path.mkdir()

    apt_path.joinpath("71_no_recommended.tt2").write_text(
        """
APT::Install-Recommends "0";
"""
    )

    apt_path.joinpath("71_no_recommended.customtt.tt2").write_text(
        """
# generated via customtt without patch file
APT::Install-Recommends "2";
"""
    )

    expected_output = """
APT::Install-Recommends "1";
"""

    apt_path.joinpath("71_no_recommended.patchtt.tt2").write_text(
        """
--- 71_no_recommended.tt2.orig   2018-01-10 15:24:06.951855880 +0100
+++ 71_no_recommended.tt2        2018-01-10 15:27:14.891237633 +0100
@@ -1 +1 @@
-APT::Install-Recommends "0";
+APT::Install-Recommends "1";

"""
    )

    apt_path.joinpath("71_no_recommended.customtt.tt2.sp1").write_text(
        """
# generated via customtt.sp1 without patch file
APT::Install-Recommends "3";
"""
    )

    apt_path.joinpath("71_no_recommended.patchtt.tt2.sp1").write_text(
        """
@@ -1 +1 @@
-APT::Install-Recommends "0";
+APT::Install-Recommends "3";

"""
    )

    expected_output_sp1 = """
APT::Install-Recommends "1";
"""

    dummy_path.joinpath("dummy.tt2").write_text(
        """
dome dummy template message
"""
    )

    dummy_path.joinpath("dummy.customtt.tt2").write_text(
        """
dome dummy customtt message
"""
    )

    dummy_path.joinpath("dummy.patchtt.tt2").write_text(
        """
@@ -1 +1 @@
-dome dummy template message
+dome dummy customtt message
"""
    )
    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        env=env,
    )

    assert "No patchtt files found, nothing to patch." not in out.stdout
    assert (
        "Validating patch '" + str(apt_path) + "/71_no_recommended.patchtt.tt2'"
        in out.stdout
    )
    assert (
        "Validating patch '" + str(apt_path) + "/71_no_recommended.patchtt.tt2.sp1'"
        in out.stdout
    )
    assert "Validating patch '" + str(dummy_path) + "/dummy.patchtt.tt2'" in out.stdout
    assert (
        "Applying patch '" + str(apt_path) + "/71_no_recommended.patchtt.tt2'"
        in out.stdout
    )
    assert (
        "Successfully created '" + str(apt_path) + "/71_no_recommended.customtt.tt2'"
        in out.stdout
    )
    assert (
        "Applying patch '" + str(apt_path) + "/71_no_recommended.patchtt.tt2.sp1'"
        in out.stdout
    )
    assert (
        "Successfully created '"
        + str(apt_path)
        + "/71_no_recommended.customtt.tt2.sp1'"
        in out.stdout
    )
    assert "Applying patch '" + str(dummy_path) + "/dummy.patchtt.tt2'" in out.stdout
    assert (
        "Successfully created '" + str(dummy_path) + "/dummy.customtt.tt2'"
        in out.stdout
    )
    assert "Requested patchtt operation has finished successfully." in out.stdout
    assert (
        "Generating "
        + str(out.env["OUTPUT_DIRECTORY"])
        + "/etc/apt/apt.conf.d/71_no_recommended: OK"
        in out.stdout
    )
    assert out.returncode == 0

    generated_customtt = apt_path.joinpath("71_no_recommended.customtt.tt2")
    generated_customtt.read_text() == expected_output

    generated_customtt = apt_path.joinpath("71_no_recommended.customtt.tt2.sp1")
    generated_customtt.read_text() == expected_output_sp1

    generated_config = out.env["OUTPUT_DIRECTORY"].joinpath(
        "etc/apt/apt.conf.d/71_no_recommended"
    )
    assert generated_config.read_text() == expected_output


@pytest.mark.tt_24920
def test_patch_action_customtt_does_not_trigger_patch_file(ngcpcfg, ngcpcfgcli):
    # ensure here new patch functionality on "ngcpcfg build"
    # will NOT affect current customtt logic if no patchtt file available

    env, cfg = ngcpcfg()
    template_pool = Path(cfg["TEMPLATE_POOL_BASE"]).joinpath("etc")
    shutil.rmtree(template_pool)
    apt_path = template_pool.joinpath("apt/apt.conf.d")
    apt_path.mkdir(parents=True, exist_ok=True)

    apt_path.joinpath("71_no_recommended.tt2").write_text(
        """
APT::Install-Recommends "0";
"""
    )

    expected_output = """
# generated via customtt without patch file
APT::Install-Recommends "1";
"""

    customtt = apt_path.joinpath("71_no_recommended.customtt.tt2").write_text(
        expected_output
    )

    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/apt/apt.conf.d/",
        env=env,
    )

    assert "No patchtt files found, nothing to patch." in out.stdout
    assert "Requested patchtt operation has finished successfully." not in out.stdout
    assert "Generating " in out.stdout
    assert "/etc/apt/apt.conf.d/71_no_recommended: OK" in out.stdout
    assert "Validating patch" not in out.stdout
    assert "71_no_recommended.customtt.tt2" not in out.stdout
    assert out.returncode == 0

    generated_config = out.env["OUTPUT_DIRECTORY"].joinpath(
        "etc/apt/apt.conf.d/71_no_recommended"
    )
    assert generated_config.read_text() == expected_output


@pytest.mark.tt_24920
def test_patch_action_build_patch_cannot_apply(ngcpcfg, ngcpcfgcli):
    # ensure 'ngcpcfg build' will be aborted if patch cannot be applied

    env, cfg = ngcpcfg()
    template_pool = Path(cfg["TEMPLATE_POOL_BASE"]).joinpath("etc")
    shutil.rmtree(template_pool)
    apt_path = template_pool.joinpath("apt/apt.conf.d")
    apt_path.mkdir(parents=True, exist_ok=True)

    apt_path.joinpath("71_no_recommended.tt2").write_text(
        """
APT::Install-Recommends "0";
"""
    )

    apt_path.joinpath("71_no_recommended.patchtt.tt2").write_text(
        """
--- 71_no_recommended.tt2.orig  2017-12-08 13:31:49.763402557 +0100
+++ 71_no_recommended.tt2       2017-12-08 13:32:00.559382702 +0100
@@ -1,2 +1 @@
-
-bla-bla-bla
+bla-bla-bla-bla
"""
    )

    out = ngcpcfgcli(
        "build",
        "--ignore-branch-check",
        "/etc/apt/apt.conf.d/",
        env=env,
    )

    assert (
        "Validating patch '" + str(apt_path) + "/71_no_recommended.patchtt.tt2'"
        in out.stdout
    )
    assert (
        "Error: The patch '"
        + str(apt_path)
        + "/71_no_recommended.patchtt.tt2' cannot be applied"
        in out.stderr
    )
    assert (
        "Error: Some operations above finished with an error for the file(s)"
        in out.stderr
    )
    assert "Requested patchtt operation has finished successfully." not in out.stdout
    assert "Generating " not in out.stdout
    assert "/etc/apt/apt.conf.d/71_no_recommended: OK" not in out.stdout
    assert out.returncode != 0


###############################################################################
# tests for "ngcpcfg patch --from-customtt"
###############################################################################


@pytest.mark.tt_24920
def test_patch_action_from_customtt_files(ngcpcfg, ngcpcfgcli):
    # Ensure here "ngcpcfg patch --from-customtt" will:
    #   * find all available customtt file
    #   * create all necessary patchtt files

    env, cfg = ngcpcfg()
    template_path = Path(cfg["TEMPLATE_POOL_BASE"]).joinpath("etc")
    shutil.rmtree(template_path)
    apt_path = template_path.joinpath("apt/apt.conf.d")
    apt_path.mkdir(parents=True, exist_ok=True)

    apt_path.joinpath("71_no_recommended.tt2").write_text(
        """
# some comment
APT::Install-Recommends "0";
"""
    )

    apt_path.joinpath("71_no_recommended.customtt.tt2").write_text(
        """
# some comment
APT::Install-Recommends "2";
"""
    )

    template_path.joinpath("expected_patch.diff").write_text(
        """@@ -1,3 +1,3 @@
 
 # some comment
-APT::Install-Recommends "0";
+APT::Install-Recommends "2";
"""
    )

    out = ngcpcfgcli(
        "patch",
        "--from-customtt",
        env=env,
    )

    assert "No patchtt files found, nothing to patch." not in out.stdout
    assert (
        "Validating customtt '" + str(apt_path) + "/71_no_recommended.customtt.tt2'"
        in out.stdout
    )
    assert (
        "Creating patchtt file '" + str(apt_path) + "/71_no_recommended.patchtt.tt2'"
        in out.stdout
    )
    assert "Requested customtt operation has finished successfully." in out.stdout
    assert out.returncode == 0

    generated_patchtt = apt_path.joinpath("71_no_recommended.patchtt.tt2")
    expected_patchtt = template_path.joinpath("expected_patch.diff")
    check_output(str(expected_patchtt), str(generated_patchtt))


@pytest.mark.tt_24920
def test_patch_action_from_customtt_missing_file_argument(ngcpcfg, ngcpcfgcli):
    # ensure "ngcpcfg patch --from-customtt missing.customtt.tt2" will be handled properly if
    # no some.customtt.tt2 file are available

    env, cfg = ngcpcfg()
    template_path = Path(cfg["TEMPLATE_POOL_BASE"]).joinpath("etc")
    shutil.rmtree(template_path)

    out = ngcpcfgcli(
        "patch",
        "--from-customtt",
        "missing.customtt.tt2",
        env=env,
    )

    assert "No customtt files found, nothing to patch." in out.stdout
    assert "Creating patchtt file '" not in out.stdout
    assert out.returncode == 0


@pytest.mark.tt_24920
def test_patch_action_from_customtt_filename_only(ngcpcfg, ngcpcfgcli):
    # ensure "ngcpcfg patch --from-customtt valid.customtt.tt2" will be handled properly if
    # no filename only valid.customtt.tt2 has been passed instead of full path

    env, cfg = ngcpcfg()
    template_path = Path(cfg["TEMPLATE_POOL_BASE"]).joinpath("etc")
    shutil.rmtree(template_path)
    apt_path = template_path.joinpath("apt/apt.conf.d")
    apt_path.mkdir(parents=True, exist_ok=True)

    apt_path.joinpath("71_no_recommended.tt2").write_text(
        """
# some comment
APT::Install-Recommends "0";
"""
    )

    apt_path.joinpath("71_no_recommended.customtt.tt2").write_text(
        """
# some comment
APT::Install-Recommends "2";
"""
    )

    template_path.joinpath("expected_patch.diff").write_text(
        """@@ -1,3 +1,3 @@
 
 # some comment
-APT::Install-Recommends "0";
+APT::Install-Recommends "2";
"""
    )

    out = ngcpcfgcli(
        "patch",
        "--from-customtt",
        "71_no_recommended.customtt.tt2",
        env=env,
    )

    assert "No patchtt files found, nothing to patch." not in out.stdout
    assert (
        "Validating customtt '" + str(apt_path) + "/71_no_recommended.customtt.tt2'"
        in out.stdout
    )
    assert (
        "Creating patchtt file '" + str(apt_path) + "/71_no_recommended.patchtt.tt2'"
        in out.stdout
    )
    assert "Requested customtt operation has finished successfully." in out.stdout
    assert out.returncode == 0

    generated_patchtt = apt_path.joinpath("71_no_recommended.patchtt.tt2")
    expected_patchtt = template_path.joinpath("expected_patch.diff")
    check_output(str(expected_patchtt), str(generated_patchtt))


@pytest.mark.tt_24920
def test_patch_action_from_customtt_missing_templates(ngcpcfg, ngcpcfgcli):
    # ensure "ngcpcfg patch --from-customtt" will be aborted if template is missing for customtt

    env, cfg = ngcpcfg()
    template_path = Path(cfg["TEMPLATE_POOL_BASE"]).joinpath("etc")
    shutil.rmtree(template_path)
    apt_path = template_path.joinpath("apt/apt.conf.d")
    apt_path.mkdir(parents=True, exist_ok=True)

    apt_path.joinpath("71_no_recommended.customtt.tt2").write_text(
        """
the content here doesn't matter as no tt2 file available
"""
    )

    out = ngcpcfgcli(
        "patch",
        "--from-customtt",
        env=env,
    )

    assert (
        "Validating customtt '" + str(apt_path) + "/71_no_recommended.customtt.tt2'"
        in out.stdout
    )
    assert (
        "Error: Missing template for customtt '"
        + str(apt_path)
        + "/71_no_recommended.customtt.tt2'"
        in out.stderr
    )
    assert (
        "Error: Some operations above finished with an error for the file(s)"
        in out.stderr
    )
    assert "Requested patchtt operation has finished successfully." not in out.stdout
    assert out.returncode != 0
