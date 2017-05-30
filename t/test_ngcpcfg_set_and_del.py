#!/usr/bin/env py.test-3

import pytest
import re
import tempfile


@pytest.mark.tt_16903
def test_set_action_generate_dictionary(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set", str(tmpfile), "aaa.bbb=123")
    assert tmpfile.read() == '''---
aaa:
  bbb: 123
'''
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_16903
def test_set_action_generate_dictionary_subsection(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set", str(tmpfile), "aaa.bbb={'ccc','123','ddd','567'}")
    assert tmpfile.read() == '''---
aaa:
  bbb:
    ccc: '123'
    ddd: '567'
'''
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_16903
def test_set_action_generate_list(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write("---\n")
    out = ngcpcfgcli("set", str(tmpfile), "aaa.bbb=['ccc','123','ddd','567']")
    assert tmpfile.read() == '''---
aaa:
  bbb:
    - ccc
    - '123'
    - ddd
    - '567'
'''
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_16903
def test_set_action_add_list(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write('''---
ccc:
  pytest-was-here: true
''')
    out = ngcpcfgcli("set", str(tmpfile), "foo.bar=['ha','hi','he','ho']")
    assert tmpfile.read() == '''---
ccc:
  pytest-was-here: 'true'
foo:
  bar:
    - ha
    - hi
    - he
    - ho
'''
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0


@pytest.mark.tt_16903
def test_set_action_modify_list(ngcpcfgcli, tmpdir):
    tmpfile = tmpdir.join("tmpfile.txt")
    tmpfile.write('''---
foo:
  bar: 'true'
  baz: 'true'
''')
    out = ngcpcfgcli("set", str(tmpfile), "foo.bar=\'false\'")
    assert tmpfile.read() == '''---
foo:
  bar: 'false'
  baz: 'true'
'''
    assert "" in out.stdout
    assert "" in out.stderr
    assert out.returncode == 0
