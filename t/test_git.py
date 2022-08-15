#!/usr/bin/env py.test-3

import os
import pytest
import re


def test_add_file_to_default_repo(cli, gitrepo):
    src = "default-git-repository.tar.gz"

    with gitrepo.from_archive(src) as git:
        # required for git versions >=2.35.2
        os.chown(git.root, os.getuid(), os.getgid())
        # required for git versions >=2.37.2
        os.chown(str(git.root) + "/.git", os.getuid(), os.getgid())

        # ensure we have valid user information
        git.config("--local", "user.email", "pytest@example.com")
        git.config("--local", "user.name", "pytest")

        # debug information, visible only in case of errors
        print("Using git {}".format(git.version))

        # git status
        ex, out, err = git.status()
        assert ex == 0
        assert "On branch" in out

        # create new file
        newfile = os.path.join(git.root, "newfile")
        with open(newfile, "w") as fd:
            fd.write('#!/bin/sh\necho "Hello World"\n')

        # adding file to repository
        assert git.branch == "master"
        git.add(newfile)
        git.commit("-m", "Adding a new file")

        # checking log
        ex, out, err = git.log()
        assert ex == 0
        assert "Adding a new file" in out


@pytest.mark.tt_11776
def test_status_output(cli, gitrepo):
    # we mock an existing repository by loading it from the default archive
    with gitrepo.from_archive(gitrepo.default) as git:
        # required for git versions >=2.35.2
        os.chown(git.root, os.getuid(), os.getgid())
        # required for git versions >=2.37.2
        os.chown(str(git.root) + "/.git", os.getuid(), os.getgid())

        # now we work with "existing" repository with path given in git.root
        with gitrepo.in_folder(git.root) as git:
            ex, out, err = git.status()
            assert ex == 0
            # git >=v2.9.3 uses "working tree",
            # before it was "working directory"
            regex = re.compile(r"nothing to commit, working (tree|directory)")
            assert re.search(regex, out)

            ex, out, error = git.status("--porcelain=v2")
            assert out == ""
            assert error == ""
            assert ex == 0

            # create new file
            newfile = os.path.join(git.root, "newfile")
            with open(newfile, "w") as fd:
                fd.write('#!/bin/sh\necho "Hello World"\n')

            ex, out, error = git.status("--porcelain=v2")
            assert out == """? newfile\n"""
            assert error == ""
            assert ex == 0
