#!/usr/bin/env python3

import pytest
import os.path
import contextlib
import filecmp
from difflib import unified_diff


@contextlib.contextmanager
def keep_directory():
    """Restore the current working directory when finished."""
    cwd = os.getcwd()
    try:
        yield
    finally:
        os.chdir(cwd)


def check_output(output_file, test_file):
    assert os.path.exists(output_file)
    assert os.path.exists(test_file)

    if not filecmp.cmp(output_file, test_file):
        with open(output_file) as out, open(test_file) as test:
            diff = unified_diff(
                out.readlines(),
                test.readlines(),
                fromfile=output_file,
                tofile=test_file,
            )
            for line in diff:
                print(line, end="")
        assert filecmp.cmp(output_file, test_file)


def check_stdoutput(stdout, test_file, tmpdir):
    output_file = os.path.join(tmpdir, "check.txt")
    with open(output_file, "w") as out_file:
        out_file.writelines(stdout)
    check_output(output_file, test_file)