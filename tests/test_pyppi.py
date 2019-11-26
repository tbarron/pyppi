from pyppi import version
import pyppi.__main__ as pmain
import glob
from importlib import import_module
import inspect
import pytest
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
                if doc_missing(mthobj) and mthname not in missing_doc:
                    missing_doc.append("{}.{}".format(name, mthname))

        for name, obj in inspect.getmembers(mod, inspect.isfunction):
            if doc_missing(obj) and name not in missing_doc:
                missing_doc.append("{}.{}".format(mname, name))

    if missing_doc:
        pytest.fail("Items missing __doc__:\n   " + "\n   ".join(missing_doc))


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
    """
    """
    pytest.dbgfunc()




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
    if not hasattr(obj, '__doc__') or obj.__doc__ is None:
        return True
    else:
        return False


# ==TAGGABLE==
