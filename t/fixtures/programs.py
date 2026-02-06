import pytest
from os import chown, getuid, getgid
from pathlib import Path
import subprocess
import sys
from collections import namedtuple
import configparser
import shutil
import re
import pprint

ProcessResult = namedtuple(
    "ProcessResult", ["returncode", "stdout", "stderr", "env", "cfg"]
)

EMPTY_GIT = Path("empty-git-repository.tar.gz").resolve()
CWD = Path().resolve()
CODE = Path("..").resolve()
FAKE_BIN = Path("fixtures/bin").resolve()
READ_CFG = Path("fixtures/read_cfg.sh").resolve()
DEFAULT_CFG = Path("fixtures/ngcpcfg.cfg").resolve()
CFG_KEYS = [
    "NGCPCTL_CONFIG",
    "NODE_CONFIG",
    "PAIR_CONFIG",
    "HOST_CONFIG",
    "LOCAL_CONFIG",
    "SITES_DIR",
    "SITES_CONFIG",
    "CONSTANTS_CONFIG",
    "MAINTENANCE_CONFIG",
    "NETWORK_CONFIG",
    "TEMPLATE_INSTANCES",
    "EXTRA_CONFIG_DIR",
]
POOL_KEYS = [
    "TEMPLATE_POOL_BASE",
    "SERVICES_POOL_BASE",
]
CFG_EXTRA = [
    "NGCPCTL_BASE",
    "NGCPCTL_MAIN",
    "STATE_FILES_DIR",
    "RUN_DIR",
]


def read_cfg(cfg_path, env):
    cmd = [READ_CFG, cfg_path]
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        env=env,
    )
    stdout, stderr = p.communicate(timeout=30)
    assert p.returncode == 0
    cfg = configparser.ConfigParser()
    cfg.read_string(stdout)
    return cfg


def gen_cfg(cfg, ngcpctl_dir):
    cfg_path = Path(ngcpctl_dir).joinpath("ngcpcfg.cfg")
    print("---- ngcpcfg.cfg -----")
    with cfg_path.open("w") as file:
        for key in cfg.options("ngcpcfg"):
            val = cfg.get("ngcpcfg", key, raw=True)
            line = '{}="{}"'.format(key.upper(), str(val))
            print(line)
            file.write("{}\n".format(line))
    return cfg_path


def copy_tree(base, src, dst_dir):
    src_path = Path(src)
    try:
        src_relative = src_path.relative_to(base)
    except ValueError:
        return None
    dst = dst_dir.joinpath(src_relative)
    if src_path.is_file():
        if dst.exists():
            return None
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, dst)
    elif src_path.is_dir():
        shutil.copytree(str(src_path), str(dst), dirs_exist_ok=True)
    return (src_relative, dst)


@pytest.fixture()
def ngcpcfg(gitrepo, tmpdir, *args):
    fakehome = Path(tmpdir.mkdir("fakehome")).resolve()
    outdir = Path(tmpdir.mkdir("ngcp-pytest-output"))
    basedir = outdir.joinpath("etc")
    basedir.mkdir()
    rundir = Path(tmpdir.mkdir("ngcp-pytest-rundir"))
    statedir = Path(tmpdir.mkdir("var-lib-ngcpcfg-state"))
    ngcpctl_dir = Path(
        gitrepo.extract_archive(
            "basic-ngcp-config.tar.gz", tmpdir.mkdir("ngcpctl-pytest-base")
        )
    ).joinpath("ngcp-config")

    def define_env(env={}):
        testenv = {
            "DEBUG": "1",
            "PATH": "{}:/usr/bin:/bin:/usr/sbin:/sbin".format(FAKE_BIN),
            "FUNCTIONS": "{}/functions/".format(CODE),
            "NGCPCFG": DEFAULT_CFG,
            "SCRIPTS": "{}/scripts/".format(CODE),
            "HELPER": "{}/helper/".format(CODE),
            "HOOKS": "{}/hooks/".format(CODE),
            "PERL5LIB": "{}/lib/".format(CODE),
            "NGCP_TESTSUITE": "true",
            "NGCP_BASE_TT2": CWD,
            "NO_DB_SYNC": "true",
            "HOME": fakehome,
            "SKIP_UPDATE_PERMS": "true",
            "SKIP_RESTORE_PERMS": "true",
            "OUTPUT_DIRECTORY": outdir,
            "STATE_FILES_DIR": statedir,
            "RUN_DIR": rundir,
        }
        testenv.update(env)
        # for now we only support TEMPLATE_POOL_BASE
        if "TEMPLATE_POOL_BASE" in testenv:
            if (
                "SERVICES_POOL_BASE" not in testenv
                or testenv["TEMPLATE_POOL_BASE"]
                != testenv["SERVICES_POOL_BASE"]
            ):
                testenv["SERVICES_POOL_BASE"] = testenv["TEMPLATE_POOL_BASE"]
                print(
                    "forced SERVICES_POOL_BASE={}".format(
                        testenv["SERVICES_POOL_BASE"]
                    )
                )
        # this has to be absolute
        testenv["NGCPCFG"] = Path(testenv["NGCPCFG"]).resolve()
        return testenv

    def process_pool(env, cfg, git):
        key_base = "TEMPLATE_POOL_BASE"
        dst_pool = ngcpctl_dir.joinpath("templates")

        if key_base in env:
            shutil.rmtree(dst_pool)
            print("removed {}".format(dst_pool))

        src = cfg.get("ngcpcfg", key_base)
        copy_tree(src, src, dst_pool)
        cfg.set("ngcpcfg", key_base, str(dst_pool))

        # required for git versions >=2.35.2
        chown(ngcpctl_dir, getuid(), getgid())
        # required for git versions >=2.37.2
        chown(str(ngcpctl_dir) + "/.git", getuid(), getgid())

        ex, out, err = git.add("templates")
        assert ex == 0
        # print("{}\nstdout:\n{}stderr:{}\n".format("git add", out, err))
        env[key_base] = cfg.get("ngcpcfg", key_base)
        # for now we only support TEMPLATE_POOL_BASE
        env["SERVICES_POOL_BASE"] = env[key_base]
        cfg.set("ngcpcfg", "SERVICES_POOL_BASE", str(dst_pool))
        # each CONFIG_TOOL dir has to be a git repository
        for dir in cfg.get("ngcpcfg", "CONFIG_POOL").split(" "):
            dir_path = Path(outdir).joinpath(dir[1:])
            print("create empty git repository at {}".format(dir_path))
            gitrepo.extract_archive(str(EMPTY_GIT), dir_path)
            # required for git versions >=2.35.2
            chown(dir_path, getuid(), getgid())
            # required for git versions >=2.37.2
            chown(str(dir_path) + "/.git", getuid(), getgid())

    def process_conf(env, cfg, git):
        base = Path(cfg.get("ngcpcfg", "NGCPCTL_MAIN"))
        for key in CFG_KEYS:
            try:
                src = cfg.get("ngcpcfg", key)
                if len(src) > 0:
                    res = copy_tree(base, src, ngcpctl_dir)
                    if res:
                        git.add(str(res[0]))
                        cfg.set("ngcpcfg", key, str(res[1]))
                    else:
                        print("[{}] {}".format(key, src))
                        # configs need to be absolute paths
                        src_path = Path(src).resolve()
                        env[key] = src_path
                        cfg.set("ngcpcfg", key, str(src_path))
            except configparser.NoOptionError:
                print("config {} not found".format(key))
                pass
        process_pool(env, cfg, git)

    def prepare_conf(env={}):
        testenv = define_env(env)
        ngcpcfg_path = testenv["NGCPCFG"]
        if not ngcpcfg_path.is_relative_to(CWD):
            print("conf already prepared, skip")
            config = read_cfg(ngcpcfg_path, testenv)
            return testenv, config["ngcpcfg"]
        config = read_cfg(testenv["NGCPCFG"], env)

        testenv["NGCPCTL_BASE"] = basedir
        testenv["NGCPCTL_MAIN"] = ngcpctl_dir
        for key in CFG_EXTRA:
            if not isinstance(testenv[key], Path):
                testenv[key] = Path(testenv[key]).resolve()
            testenv[key].mkdir(parents=True, exist_ok=True)
            config.set("ngcpcfg", key, str(testenv[key]))

        with gitrepo.in_folder(ngcpctl_dir) as git:
            # required for git versions >=2.35.2
            chown(git.root, getuid(), getgid())
            # required for git versions >=2.37.2
            chown(str(git.root) + "/.git", getuid(), getgid())

            # ensure we have valid user information
            git.config("--local", "user.email", "pytest@example.com")
            git.config("--local", "user.name", "pytest")

            process_conf(testenv, config, git)
            # generate NGCPCFG with config values
            testenv["NGCPCFG"] = gen_cfg(config, ngcpctl_dir)
            git.add(testenv["NGCPCFG"])
            # ex, out, err = git.diff("HEAD")
            # print("{}\nstdout:\n{}stderr:{}\n".format("git diff", out, err))
            ex, out, err = git.commit("-a", "-m", "prepare_conf done")

            # for debugging underlying problems like safe.directory situation
            # print("debug: git show: {}\n"
            # .format(subprocess.getoutput("git show")))
            print("{}\nstdout:\n{}stderr:{}\n".format("git commit", out, err))
            assert ex == 0
        return testenv, config["ngcpcfg"]

    return prepare_conf


@pytest.fixture()
def ngcpcfgcli(ngcpcfg, *args):
    """Execute ``ngcpcfg``."""

    def run(*args, env={}):
        testenv, cfg = ngcpcfg(env)

        # if we're already running under root don't execute under fakeroot,
        # causing strange problems when debugging execution e.g. via strace
        if getuid() == 0:
            fakeroot = []
        else:
            fakeroot = ["fakeroot"]
        config = "{}/sbin/ngcpcfg".format(CODE)
        p = subprocess.Popen(
            fakeroot + [config] + list(args),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=testenv,
        )
        stdout, stderr = p.communicate(timeout=30)

        # debug, only printed in logs in case of error
        print("env:")
        pprint.pprint(testenv)
        print("stdout:")
        print(stdout)
        print("stderr:")
        print(stderr)

        result = ProcessResult(p.returncode, stdout, stderr, testenv, cfg)
        return result

    return run


@pytest.fixture()
def helpercli(tmpdir, *args):
    """Execute a helper directly"""
    helper_base = "{}/helper/{}"
    fakehome = Path(tmpdir.mkdir("fakehome")).resolve()

    def run(helper, *args, env={}):
        testenv = {
            "PATH": "{}:/usr/bin:/bin:/usr/sbin:/sbin".format(FAKE_BIN),
            "PERL5LIB": "{}/lib/".format(CODE),
            "NGCP_TESTSUITE": "true",
            "HOME": fakehome,
        }
        testenv.update(env)

        # if we're already running under root don't execute under fakeroot,
        # causing strange problems when debugging execution e.g. via strace
        if getuid() == 0:
            fakeroot = []
        else:
            fakeroot = ["fakeroot"]

        p = subprocess.Popen(
            fakeroot + [helper_base.format(CODE, helper)] + list(args),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            env=testenv,
        )
        stdout, stderr = p.communicate(timeout=30)

        # debug, only printed in logs in case of error
        print("env:")
        pprint.pprint(testenv)
        print("stdout:")
        print(stdout)
        print("stderr:")
        print(stderr)

        result = namedtuple(
            "ProcessResult", ["returncode", "stdout", "stderr"]
        )(p.returncode, stdout, stderr)
        return result

    return run
