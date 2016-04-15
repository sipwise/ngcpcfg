#!/usr/bin/env python3

import pytest
import os.path
import contextlib


@contextlib.contextmanager
def keep_directory():
    """Restore the current working directory when finished.

    Originally written by vincentbernat:
      https://github.com/vincentbernat/lldpd/blob/master/tests/integration/fixtures/namespaces.py
    """
    cwd = os.getcwd()
    try:
        yield
    finally:
        os.chdir(cwd)
