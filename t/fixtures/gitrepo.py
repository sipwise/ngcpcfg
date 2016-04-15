#!/usr/bin/env python3

import os
import shutil
import pytest
import tarfile
import zipfile
import tempfile

from .commandline import run
from .fs import keep_directory


BUILTIN_GIT_COMMANDS = {"au", "co", "df", "gr", "grl", "last", "lg", "sa", "st", "add", "am", "archive", "bisect", "branch", "bundle", "checkout", "cherry-pick", "citool", "clean", "clone", "commit", "describe", "diff", "fetch", "format-patch", "gc", "grep", "gui", "init", "log", "merge", "mv", "notes", "pull", "push", "rebase", "reset", "revert", "rm", "shortlog", "show", "stash", "status", "submodule", "tag", "config", "fast-export", "fast-import", "filter-branch", "mergetool", "pack-refs", "prune", "reflog", "relink", "remote", "repack", "replace", "blame", "cherry", "count-objects", "difftool", "fsck", "get-tar-commit-id", "help", "instaweb", "merge-tree", "rerere", "rev-parse", "show-branch", "verify-commit", "verify-tag", "whatchanged", "archimport", "cvsexportcommit", "cvsimport", "cvsserver", "imap-send", "quiltimport", "request-pull", "send-email", "svn", "apply", "checkout-index", "commit-tree", "hash-object", "index-pack", "merge-file", "merge-index", "mktag", "mktree", "pack-objects", "prune-packed", "read-tree", "symbolic-ref", "unpack-objects", "update-index", "update-ref", "write-tree", "cat-file", "diff-files", "diff-index", "diff-tree", "for-each-ref", "ls-files", "ls-remote", "ls-tree", "merge-base", "name-rev", "pack-redundant", "rev-list", "show-index", "show-ref", "unpack-file", "var", "verify-pack", "daemon", "fetch-pack", "http-backend", "send-pack", "update-server-info", "http-fetch", "http-push", "parse-remote", "receive-pack", "shell", "upload-archive", "upload-pack", "completing", "check-attr", "check-ignore", "check-mailmap", "check-ref-format", "fmt-merge-msg", "mailinfo", "mailsplit", "merge-one-file", "patch-id", "stripspace"}

# helpers

def create_tmp_folder():
    """Create and return a unique temporary folder"""
    return tempfile.mkdtemp(prefix='ngcp-', suffix='-pytest')

def delete_tmp_folder(folder):
    """Recursively delete a folder"""
    shutil.rmtree(folder)

def find_git_root(folder):
    """If `folder` contains one folder, return this folder. Otherwise `folder`"""
    children = os.listdir(folder)
    if len(children) > 1:
        return folder
    else:
        return os.path.join(folder, children[0])


# implementation

class GitCommand:
    def __init__(self, repo, command):
        self.repo = repo
        self.command = command

    def __call__(self, *args):
        with keep_directory():
            os.chdir(self.repo.root)
            return run('git', self.command, *args)

    def __repr__(self):
        return "command 'git {}'".format(self.command)


class GitRepository:
    """Represents a git repository we are working with"""

    def __init__(self, root, delete_fn=None):
        self.root = root
        self.delete_fn = delete_fn

    def __getattr__(self, name):
        if name not in BUILTIN_GIT_COMMANDS:
            raise ValueError("git command '{}' is unknown".format(name))
        return GitCommand(self, name)

    def __enter__(self):
        return self

    def __exit__(self, *exc_details):
        if self.delete_fn:
            self.delete_fn()

    @property
    def branch(self):
        """Return current git branch"""
        ex, out, err = GitCommand(self, 'branch')()
        assert ex == 0
        for line in out.splitlines():
            if line.startswith('*'):
                return line[1:].strip()

    @property
    def version(self):
        """Return git version in use"""
        ex, out, err = GitCommand(self, '--version')()
        assert ex == 0
        return ' '.join(out.strip().split()[2:])

    def __repr__(self):
        return "GitRepository at '{}'".format(self.root)


class GitLoader:
    """Provides methods to download a git repository"""
    default = 'default-git-repository.tar.gz'

    def __init__(self):
        self.localpath = create_tmp_folder()

    @staticmethod
    def extract_archive(src, dest):
        """Extract files and folder in archive `src` to path `dest`"""
        suffix = None
        if src.endswith('.tgz') or src.endswith('.tar.gz'):
            suffix = ':gz'
        elif src.endswith('.tbz2') or src.endswith('.tar.bz2'):
            suffix = ':bz2'
        elif src.endswith('.tar.lzma'):
            suffix = ':xz'
        elif src.endswith('.tar'):
            suffix = ''

        if suffix is not None:
            ar = tarfile.open(src, 'r' + suffix)
            ar.extractall(path=dest)
            return dest
        elif src.endswith('.zip'):
            with zipfile.ZipFile(src, 'r') as fd:
                fd.extractall(path=dest)
            return dest
        else:
            raise ValueError('Archive of unknown file type: {}'.format(src))

    def from_url(self, url):
        """Clone git repository from URL"""
        ex, out, err = cli.run('git', 'clone', url, self.localpath)
        assert ex == 0
        return GitRepository(find_git_root(self.localpath), delete_fn=self.cleanup)

    def from_archive(self, archive_path):
        """Extract git repository from given archive"""
        self.localpath = self.extract_archive(archive_path, self.localpath)
        return GitRepository(find_git_root(self.localpath), delete_fn=self.cleanup)

    def in_folder(self, path):
        """Assume `path` already contains a git repository"""
        assert os.path.exists(os.path.join(path, '.git')), \
            '.git folder must exist in git repository'
        return GitRepository(path)

    def cleanup(self):
        delete_tmp_folder(self.localpath)

    def __repr__(self):
        return "GitLoader for '{}'".format(self.localpath)


@pytest.fixture()
def gitrepo():
    return GitLoader()
