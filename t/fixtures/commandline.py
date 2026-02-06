#!/usr/bin/env python3

import pytest
import functools
import subprocess
import collections

ProcessResult = collections.namedtuple(
    "ProcessResult", ["exitcode", "stdout", "stderr"]
)


def run(
    *args,
    env=None,
    timeout=None,
    stdin=None,
    expect_stdout=True,
    expect_stderr=True,
    outencoding="utf-8",
    errencoding="utf-8",
):
    """Execute command in `args` in a subprocess"""

    # drop stdout & stderr and spare some memory, if not needed
    stdout = subprocess.PIPE
    if not expect_stdout:
        stdout = None

    stderr = subprocess.PIPE
    if not expect_stderr:
        stderr = None

    # run command
    p = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    if stdin:
        p.stdin.write(stdin)
    stdout, stderr = p.communicate(timeout=timeout)

    # decode output
    if expect_stdout and stdout:
        stdoutput = stdout.decode(outencoding)
    else:
        stdoutput = ""
    if expect_stderr and stderr:
        stderror = stderr.decode(errencoding)
    else:
        stderror = ""

    return ProcessResult(p.returncode, stdoutput, stderror)


@pytest.fixture()
def cli():
    """Run a command as subprocess.
    Returns a namedtuple with members (stdout, stderr, exitcode).

    :param env:             a dictionary of environment variables
    :param timeout:         maximum number of seconds before
                            TimeoutError is raised
    :param stdin:           bytes-object to write to stdin once the
                            program has started
    :param expect_stdout:   shall stdout be provided in the result?
    :param outencoding:     encoding to decode stdout
    :param expect_stderr:   shall stderr be provided in the result?
    :param errencoding:     encoding to decode stderr
    """
    return run
