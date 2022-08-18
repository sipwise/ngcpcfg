#!/usr/bin/env py.test-3

import pytest

###############################################################
#  ngcpcfg set
###############################################################


@pytest.mark.tt_16903
def test_set_action_missing_all_parameters(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set")
    assert tmpfile.read() == """---\n"""
    assert "" in out.stdout
    assert "Usage: ngcpcfg set [<options>] <file> <key>" in out.stderr
    assert out.returncode == 1


@pytest.mark.tt_16903
def test_set_action_missing_first_parameter(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set", "test=123")
    assert tmpfile.read() == """---\n"""
    assert "" in out.stdout
    assert "Usage: ngcpcfg set [<options>] <file> <key>" in out.stderr
    assert out.returncode == 1


@pytest.mark.tt_16903
def test_set_action_missing_second_parameter(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set", str(tmpfile))
    assert tmpfile.read() == """---\n"""
    assert "" in out.stdout
    assert "Usage: ngcpcfg set [<options>] <file> <key>" in out.stderr
    assert out.returncode == 1


@pytest.mark.tt_16903
def test_set_action_missing_option_value(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set", str(tmpfile), "aaa.bbb=")
    assert tmpfile.read() == """---\n"""
    assert "" in out.stdout
    assert "Error: missing value to set. Exiting." in out.stderr
    assert out.returncode == 1


@pytest.mark.tt_16903
def test_set_action_missing_option_name(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set", str(tmpfile), "=123")
    assert tmpfile.read() == """---\n"""
    assert "" in out.stdout
    assert "Error: missing option to set. Exiting." in out.stderr
    assert out.returncode == 1


@pytest.mark.tt_16903
def test_set_action_missing_file(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set", "/tmp/non_existed_file", "aaa=123")
    assert tmpfile.read() == """---\n"""
    assert "" in out.stdout
    assert "Error: missing /tmp/non_existed_file. Exiting." in out.stderr
    assert out.returncode == 1


@pytest.mark.tt_51601
def test_set_wrong_set_option(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set", "--something", str(tmpfile), "aaa=123")
    assert tmpfile.read() == """---\n"""
    assert "" in out.stdout
    assert "Error: unsupported option '--something'. Exiting." in out.stderr
    assert out.returncode == 1


@pytest.mark.tt_16903
def test_set_action_generate_dictionary_digits(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set", str(tmpfile), "aaa.bbb=123")
    assert (
        tmpfile.read()
        == """---
aaa:
  bbb: 123
"""
    )
    # TODO: check diff output on out.stdout,
    # currently it is empty as 'ngcpcfg diff' has no
    # output due to missing git/etckeeper/commits for git diff.
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_51601
def test_set_action_generate_dictionary_digits_diff(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set", "--diff", str(tmpfile), "aaa.bbb=123")
    assert (
        tmpfile.read()
        == """---
aaa:
  bbb: 123
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_16903
def test_set_action_generate_dictionary_digits_equal_sign(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set", str(tmpfile), "aaa.bbb=ccc=123")
    assert (
        tmpfile.read()
        == """---
aaa:
  bbb: ccc=123
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_16903
def test_set_action_generate_dictionary_bool_fail(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set", str(tmpfile), "aaa.bbb=true")
    assert (
        tmpfile.read()
        == """---
aaa:
  bbb: 'true'
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_16903
def test_set_action_generate_dictionary_bool_ok(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set", str(tmpfile), "aaa.bbb='true'")
    assert (
        tmpfile.read()
        == """---
aaa:
  bbb: 'true'
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_16903
def test_set_action_generate_dictionary_string(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set", str(tmpfile), "aaa.bbb='on'")
    assert (
        tmpfile.read()
        == """---
aaa:
  bbb: on
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_16903
def test_set_action_generate_dictionary_string_change(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set", str(tmpfile), "aaa.bbb='off'")
    assert (
        tmpfile.read()
        == """---
aaa:
  bbb: off
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_16903
def test_set_action_generate_dictionary_string_nochange(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set", str(tmpfile), "aaa.bbb=off")
    assert (
        tmpfile.read()
        == """---
aaa:
  bbb: off
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_16903
def test_set_action_generate_dictionary_subsection(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set", str(tmpfile), "aaa.bbb={'ccc','123','ddd','567'}")
    assert (
        tmpfile.read()
        == """---
aaa:
  bbb:
    ccc: '123'
    ddd: '567'
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_33030
def test_set_action_overwrite_dictionary_subsection(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write(
        """---
aaa:
  bbb:
    eee: 'foobar'
    fff: 'quux'
"""
    )
    out = ngcpcfgcli("set", str(tmpfile), "aaa.bbb={'ccc','123','ddd','567'}")
    assert (
        tmpfile.read()
        == """---
aaa:
  bbb:
    ccc: '123'
    ddd: '567'
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_16903
def test_set_action_generate_list(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set", str(tmpfile), "aaa.bbb=['ccc','123','ddd','567']")
    assert (
        tmpfile.read()
        == """---
aaa:
  bbb:
  - ccc
  - '123'
  - ddd
  - '567'
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_33030
def test_set_action_overwrite_list(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write(
        """---
aaa:
  bbb:
  - 5432
  - 'foobar'
"""
    )
    out = ngcpcfgcli("set", str(tmpfile), "aaa.bbb=['ccc','123','ddd','567']")
    assert (
        tmpfile.read()
        == """---
aaa:
  bbb:
  - ccc
  - '123'
  - ddd
  - '567'
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_16903
def test_set_action_add_list(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write(
        """---
ccc:
  pytest-was-here: true
"""
    )
    out = ngcpcfgcli("set", str(tmpfile), "foo.bar=['ha','hi','he','ho']")
    assert (
        tmpfile.read()
        == """---
ccc:
  pytest-was-here: true
foo:
  bar:
  - ha
  - hi
  - he
  - ho
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_16903
def test_set_action_modify_list(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write(
        """---
foo:
  bar: 'true'
  baz: 'true'
"""
    )
    out = ngcpcfgcli("set", str(tmpfile), "foo.bar='false'")
    assert (
        tmpfile.read()
        == """---
foo:
  bar: 'false'
  baz: 'true'
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_33030
def test_set_action_set_array_element(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write(
        """---
foo:
  bar:
  - 'blah'
  - 'baz'
"""
    )
    out = ngcpcfgcli("set", str(tmpfile), "foo.bar.0='moo'")
    assert (
        tmpfile.read()
        == """---
foo:
  bar:
  - moo
  - baz
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_33030
def test_set_action_append_array_element(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write(
        """---
foo:
  bar:
  - blah
  - baz
"""
    )
    out = ngcpcfgcli("set", str(tmpfile), "foo.bar.2='moo'")
    assert (
        tmpfile.read()
        == """---
foo:
  bar:
  - blah
  - baz
  - moo
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_33030
def test_set_action_auto_append_array_element(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write(
        """---
foo:
  bar:
  - blah
  - baz
"""
    )
    out = ngcpcfgcli("set", str(tmpfile), "foo.bar.APPEND='moo'")
    assert (
        tmpfile.read()
        == """---
foo:
  bar:
  - blah
  - baz
  - moo
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_33030
def test_set_action_add_new_array_one_element(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write(
        """---
foo:
  moo: blah
"""
    )
    out = ngcpcfgcli("set", str(tmpfile), "foo.bar.0='boo'")
    assert (
        tmpfile.read()
        == """---
foo:
  bar:
  - boo
  moo: blah
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_33030
def test_set_action_set_array_subelement(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write(
        """---
foo:
  bar:
  - blah: quux
    foo: meh
  - blah: zarg
    foo: ruuk
  moo: blah
"""
    )
    out = ngcpcfgcli("set", str(tmpfile), "foo.bar.1.foo='boo'")
    assert (
        tmpfile.read()
        == """---
foo:
  bar:
  - blah: quux
    foo: meh
  - blah: zarg
    foo: boo
  moo: blah
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_33030
def test_set_action_set_hash_instead_of_array(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write(
        """---
foo:
  bar:
  - blah: quux
    foo: meh
  - blah: zarg
    foo: ruuk
  moo: blah
"""
    )
    out = ngcpcfgcli("set", str(tmpfile), "foo.bar.baz=123")
    assert (
        tmpfile.read()
        == """---
foo:
  bar:
  - blah: quux
    foo: meh
  - blah: zarg
    foo: ruuk
  moo: blah
"""
    )
    assert "" in out.stdout
    assert "Key resolved to a ARRAY reference; refusing to overwrite." in out.stderr
    assert out.returncode == 1


@pytest.mark.tt_33030
def test_set_action_set_array_instead_of_scalar(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write(
        """---
foo:
  bar:
  - blah: quux
    foo: meh
  - blah: zarg
    foo: ruuk
  moo: blah
"""
    )
    out = ngcpcfgcli("set", str(tmpfile), "foo.bar=123")
    assert (
        tmpfile.read()
        == """---
foo:
  bar:
  - blah: quux
    foo: meh
  - blah: zarg
    foo: ruuk
  moo: blah
"""
    )
    assert "" in out.stdout
    assert "Key resolved to a ARRAY reference; refusing to overwrite." in out.stderr
    assert out.returncode == 1


@pytest.mark.tt_33030
def test_set_action_set_hash_instead_of_scalar(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write(
        """---
foo:
  bar:
  - blah: quux
    foo: meh
  - blah: zarg
    foo: ruuk
  moo: blah
"""
    )
    out = ngcpcfgcli("set", str(tmpfile), "foo=123")
    assert (
        tmpfile.read()
        == """---
foo:
  bar:
  - blah: quux
    foo: meh
  - blah: zarg
    foo: ruuk
  moo: blah
"""
    )
    assert "" in out.stdout
    assert "Key resolved to a HASH reference; refusing to overwrite." in out.stderr
    assert out.returncode == 1


@pytest.mark.tt_33030
def test_set_action_check_keyword(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write(
        """---
foo:
  bar: no
"""
    )
    out = ngcpcfgcli("set", str(tmpfile), "foo.bar=yes")
    assert (
        tmpfile.read()
        == """---
foo:
  bar: yes
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


###############################################################
#  ngcpcfg del
###############################################################


@pytest.mark.tt_16903
def test_del_action_missing_all_parameters(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("del")
    assert tmpfile.read() == """---\n"""
    assert "" in out.stdout
    assert "Usage: ngcpcfg del [<options>] <file> <option>" in out.stderr
    assert out.returncode == 1


@pytest.mark.tt_16903
def test_del_action_missing_first_parameter(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("del", "test.to.be.deleted")
    assert tmpfile.read() == """---\n"""
    assert "" in out.stdout
    assert "Usage: ngcpcfg del [<options>] <file> <option>" in out.stderr
    assert out.returncode == 1


@pytest.mark.tt_16903
def test_del_action_missing_second_parameter(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("del", str(tmpfile))
    assert tmpfile.read() == """---\n"""
    assert "" in out.stdout
    assert "Usage: ngcpcfg del [<options>] <file> <option>" in out.stderr
    assert out.returncode == 1


@pytest.mark.tt_16903
def test_del_action_missing_file(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("del", "/tmp/non_existed_file", "test")
    assert tmpfile.read() == """---\n"""
    assert "" in out.stdout
    assert "Error: missing /tmp/non_existed_file. Exiting." in out.stderr
    assert out.returncode == 1


@pytest.mark.tt_51601
def test_del_wrong_del_option(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write(
        """---
aaa:
  bbb: '123'
  ccc: '456'
"""
    )
    out = ngcpcfgcli("del", "--something", str(tmpfile), "aaa.bbb")
    assert (
        tmpfile.read()
        == """---
aaa:
  bbb: '123'
  ccc: '456'
"""
    )
    assert "" in out.stdout
    assert "Error: unsupported option '--something'. Exiting." in out.stderr
    assert out.returncode == 1


@pytest.mark.tt_16903
def test_del_action_delete_child_item(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write(
        """---
aaa:
  bbb: '123'
  ccc: '456'
"""
    )
    out = ngcpcfgcli("del", str(tmpfile), "aaa.bbb")
    assert (
        tmpfile.read()
        == """---
aaa:
  ccc: '456'
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_16903
def test_del_action_delete_child_item_repeat_no_change(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write(
        """---
aaa:
  bbb: '123'
  ccc: '456'
"""
    )
    out = ngcpcfgcli("del", str(tmpfile), "aaa.bbb")
    assert (
        tmpfile.read()
        == """---
aaa:
  ccc: '456'
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_16903
def test_del_action_delete_parent_item(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write(
        """---
aaa:
  bbb: '123'
  ccc: '456'
"""
    )
    tmpfile.write("---\n")
    out = ngcpcfgcli("del", str(tmpfile), "aaa")
    assert (
        tmpfile.read()
        == """--- {}
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_16903
def test_del_action_missing_item(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write(
        """---
aaa:
  bbb: '123'
  ccc: '456'
"""
    )
    out = ngcpcfgcli("del", str(tmpfile), "aaa.ddd")
    assert (
        tmpfile.read()
        == """---
aaa:
  bbb: '123'
  ccc: '456'
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_16903
def test_del_action_typo_in_length(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write(
        """---
aaa:
  bbb: '123'
  ccc: '456'
"""
    )
    out = ngcpcfgcli("del", str(tmpfile), "aa")
    assert (
        tmpfile.read()
        == """---
aaa:
  bbb: '123'
  ccc: '456'
"""
    )
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0
