import glob
import pytest
import tbx


def test_flake():
    """
    Check code quality
    """
    pytest.dbgfunc()
    files = lglob("pyppi/*.py", "tests/*.py")
    cmd = "flake8 --ignore $FLAKE_IGNORE {}".format(" ".join(files))
    result = tbx.run(tbx.expand(cmd))
    assert result == ""


def lglob(*args, dupl_allowed=False):
    """
    glob a list of paths and return the results in a single list
    """
    rval = []
    [rval.extend(y) for y in [glob.glob(x) for x in args]]
    if not dupl_allowed:
        rval = list(set(rval))
    return rval


def test_pytest_fails_successfully():
    pytest.fail('getting started')
