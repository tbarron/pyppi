"""
This is free and unencumbered software released into the public domain.
For more information, please visit <http://unlicense.org/>.
"""
import glob
from importlib import import_module
import inspect
from py.path import local as pypath
from pyppi import version
from pyppi.__main__ import pyppi_error
import pyppi.__main__ as pmain
import pytest
import re
import sys
import tbx


# -----------------------------------------------------------------------------
def test_flake():
    """
    Check code quality
    """
    pytest.dbgfunc()
    files = lglob("pyppi/*.py", "tests/*.py")
    cmd = "flake8 --ignore $FLAKE_IGNORE {}".format(" ".join(files))
    result = tbx.run(tbx.expand(cmd))
    assert result == ""


# -----------------------------------------------------------------------------
def test_function_doc():
    """
    Verify that each of our functions have a __doc__ string
    """
    pytest.dbgfunc()

    importables = ['pyppi.__main__']
    importables.extend([tbx.basename(_).replace('.py', '')
                        for _ in glob.glob('tests/*.py')])

    missing_doc = []
    for mname in importables:
        mod = import_module(mname)
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            if doc_missing(obj) and name not in missing_doc:
                missing_doc.append(name)

            for mthname, mthobj in inspect.getmembers(obj, inspect.isfunction):
                if name in ['pypath', 'local']:
                    continue
                if doc_missing(mthobj) and mthname not in missing_doc:
                    missing_doc.append("{}.{}".format(name, mthname))

        for name, obj in inspect.getmembers(mod, inspect.isfunction):
            if doc_missing(obj) and name not in missing_doc:
                missing_doc.append("{}.{}".format(mname, name))

    if missing_doc:
        pytest.fail("Items missing __doc__:\n   " + "\n   ".join(missing_doc))


# -----------------------------------------------------------------------------
def test_pydoc():
    """
    Run pydoc pyppi and look at what we get back
    """
    pytest.dbgfunc()
    out = tbx.run("pydoc pyppi")
    exp_l = ["Build a python package index conforming to PEP 503",
             "pyppi build [-d] FILENAME",
             "Build the python package index based on the contents ",
             "pyppi version [-d]",
             "Report the pyppi version",
             ]
    for item in exp_l:
        assert item in out
    hl_out = tbx.run("python pyppi --help")
    desc = re.findall("(DESCRIPTION.*)This is free", hl_out, re.DOTALL)
    desc_l = [_ for _ in desc[0].split("\n") if not re.match(r"^\s*$", _)]
    for line in desc_l:
        assert line in out, "'{}' not in '{}'".format(line, out)


# -----------------------------------------------------------------------------
def test_help():
    """
    Run 'pyppi help' and examine the output
    """
    pytest.dbgfunc()
    out = tbx.run("python pyppi help")
    assert "USAGE:" in out
    assert "    pyppi build [-d] FILENAME" in out
    assert "    pyppi version [-d]" in out


# -----------------------------------------------------------------------------
def test_help_long():
    """
    Run 'pyppi --help' and examine the output
    """
    pytest.dbgfunc()
    out = tbx.run("python pyppi --help")
    assert "USAGE:" in out
    assert "    pyppi build [-d] FILENAME" in out
    assert "    pyppi version [-d]" in out
    assert "    Build the python package index based on" in out
    assert "    Report the pyppi version" in out
    help_out = tbx.run("python pyppi help")
    assert help_out in out


# -----------------------------------------------------------------------------
def test_read_cfg_file(tmpdir, fx_cfgfile):
    """
    Call pmain.read_cfg_file on a config file and verify the struct returned
    """
    pytest.dbgfunc()
    exp = fx_cfgfile
    cfgfile = tmpdir.join("test.cfg")
    cfg = pmain.read_cfg_file(cfgfile)                                # payload
    assert cfg == exp


# -----------------------------------------------------------------------------
def test_read_cfg_extra_root(tmpdir, fx_extra_root):
    """
    Call pmain.read_cfg_file on a config file and verify the struct returned
    """
    pytest.dbgfunc()
    cfgfile = tmpdir.join("test.cfg")
    with pytest.raises(pyppi_error) as err:
        pmain.read_cfg_file(cfgfile)                                  # payload
    assert "root was already set" in str(err.value)


# -----------------------------------------------------------------------------
def test_build_dirs_noroot(tmpdir, fx_cfgfile):
    """
    Make sure function build_dirs() creates the root directory
    """
    pytest.dbgfunc()
    data = fx_cfgfile
    root = tmpdir.join("pypi")
    assert not root.exists()
    pmain.build_dirs(data)                                            # payload
    assert root.exists()
    for pkg in data['pkglist']:
        pkgdir = root.join(pkg)
        assert pkgdir.isdir()


# -----------------------------------------------------------------------------
def test_build_dirs_withroot(tmpdir, fx_cfgfile):
    """
    Make sure function build_dirs() runs successfully if root exists
    """
    pytest.dbgfunc()
    data = fx_cfgfile
    root = tmpdir.join("pypi")
    root.ensure(dir=True)
    pmain.build_dirs(data)                                            # payload
    assert root.isdir()
    for pkg in data['pkglist']:
        pkgdir = root.join(pkg)
        assert pkgdir.isdir()


# -----------------------------------------------------------------------------
def test_build_index_htmls(tmpdir, fx_cfgfile):
    """
    After calling build_index_htmls(), verify that the expected files exist and
    have (approximately) the right content
    """
    pytest.dbgfunc()
    cfg = fx_cfgfile
    root = pypath(cfg['root'])
    pkg_d = cfg['pkglist']
    pmain.build_dirs(cfg)
    pmain.build_index_htmls(cfg)                                      # payload

    rootidx = root.join("index.html")
    assert rootidx.exists()
    assert "<!DOCTYPE html>" in rootidx.read()
    base = root.basename
    for pkgname in pkg_d:
        assert "/{}/{}/".format(base, pkgname) in rootidx.read()

        pkgidx = root.join(pkgname, "index.html")
        assert "<!DOCTYPE html>" in pkgidx.read()
        for release in pkg_d[pkgname]:
            assert release['url'] in pkgidx.read()
            assert release['version'] in pkgidx.read()
            if 'minpy' in release:
                assert release['minpy'] in pkgidx.read()


# -----------------------------------------------------------------------------
def test_debuggable():
    """
    Verify that all functions have a __doc__
    """
    pytest.dbgfunc()
    rval = ""
    func_d = dict(inspect.getmembers(sys.modules['test_pyppi'],
                                     inspect.isfunction))
    for func in func_d:
        if func.startswith('test_'):
            mem_d = dict(inspect.getmembers(func_d[func]))
            cobj = mem_d['__code__']
            if 'dbgfunc' not in cobj.co_names:
                rval += "    {}\n".format(func)
    assert rval == ""


# -----------------------------------------------------------------------------
def test_version(capsys):
    """
    Check what the pyppi_version() function returns
    """
    pytest.dbgfunc()
    kw = {'build': False, 'd': False, 'FILENAME': None, 'version': True}
    pmain.pyppi_version(**kw)                                         # payload
    (result, err) = capsys.readouterr()
    assert "pyppi version" in result
    assert version._v in result


# -----------------------------------------------------------------------------
def test_deployable():
    """
    Check that 1) no untracked files are hanging out, 2) no staged but
    uncommitted updates are outstanding, 3) no unstaged, uncommitted changes
    are outstanding, 4) the most recent git tag matches HEAD, and 5) the most
    recent git tag matches the current version.
    """
    pytest.dbgfunc()
    staged, changed, untracked = tbx.git_status()
    assert untracked == [], "You have untracked files"
    assert changed == [], "You have unstaged updates"
    assert staged == [], "You have updates staged but not committed"

    if tbx.git_current_branch() != 'master':
        return True

    last_tag = tbx.git_last_tag()
    msg = "Version ({}) does not match tag ({})".format(version._v,
                                                        last_tag)
    assert version._v == last_tag, msg
    assert tbx.git_hash() == tbx.git_hash(last_tag), "Tag != HEAD"


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_extra_root(tmpdir):
    """
    Set up a config file with an extra root line to trigger the exception
    """
    lines = ["root            foobar",
             "",
             "package         whatever",
             "    version     0.0.0",
             "    url         git+https://someplace.com/foobar/foobar/",
             "",
             "root            throwthatexception",
             "",
             ]
    tstcfg = tmpdir.join("test.cfg")
    tstcfg.write("\n".join(lines) + "\n")


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_cfgfile(tmpdir):
    """
    Set up a config file we can test read_cfg_file on
    """
    urlpfx = "git+https://github.com/tbarron"
    data = {'root': "{}/pypi".format(tmpdir.strpath),
            'pkglist':
            {'foobar': [{'version': "0.0.0",
                         'url': "{}/foobar#egg=foobar-0.0.0".format(urlpfx)},
                        {'version': "0.0.1",
                         'url': "{}/foobar#egg=foobar-0.0.1".format(urlpfx)},
                        ],
             'tbx': [{'version': "0.1.0",
                      'url': "{}/tbx#egg=tbx-0.1.0".format(urlpfx),
                      'minpy': "3.8.0"},
                     ],
             'dtm': [{'version': "2.0.0",
                      'url': "{}/dtm#egg=dtm-2.0.0".format(urlpfx)},
                     ]}
            }
    tstcfg = tmpdir.join("test.cfg")
    cfgs = "root       {}\n\n".format(data['root'])
    pkg_l = data['pkglist']
    for pkg in pkg_l:
        cfgs += "package       {}\n".format(pkg)
        for rel in pkg_l[pkg]:
            cfgs += "    version   {}\n".format(rel['version'])
            cfgs += "    url       {}\n".format(rel['url'])
            if 'minpy' in rel:
                cfgs += "    minpy     {}\n".format(rel['minpy'])
        cfgs += "\n"

    tstcfg.write(cfgs)
    return data


# -----------------------------------------------------------------------------
def lglob(*args, dupl_allowed=False):
    """
    glob a list of paths and return the results in a single list
    """
    rval = []
    [rval.extend(y) for y in [glob.glob(x) for x in args]]
    if not dupl_allowed:
        rval = list(set(rval))
    return rval


# -----------------------------------------------------------------------------
def doc_missing(obj):
    """
    Check *obj* for a non-empty __doc__ element
    """
    if any([not hasattr(obj, '__doc__'),
            obj.__doc__ is None,
            obj.__doc__.strip() == ""]):
        return True
    else:
        return False


# ==TAGGABLE==
