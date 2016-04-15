#!/usr/bin/env python3

import pytest
import os.path
import contextlib


@contextlib.contextmanager
def keep_directory():
    """Restore the current working directory when finished."""
    cwd = os.getcwd()
    try:
        yield
    finally:
        os.chdir(cwd)
