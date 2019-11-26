"""
Usage:
    pyppi build [-d] FILENAME
    pyppi version [-d]
"""
from docopt_dispatch import dispatch
import pdb
from pyppi import version
from py.path import local
import re
import tbx


# -----------------------------------------------------------------------------
@dispatch.on('build')
def pyppi_build(**kw):
    """
    Build the package index from kw['FILENAME']
    """
    conditional_debug(kw['d'])
    filename = kw['FILENAME']
    print("Reading config file {}".format(filename))
    cfg = read_cfg_file(filename)
    build_dirs(cfg)


# -----------------------------------------------------------------------------
@dispatch.on('version')
def pyppi_version(**kw):
    """
    Report this program's version
    """
    conditional_debug(kw['d'])
    print("pyppi version {}".format(version._v))


# -----------------------------------------------------------------------------
def build_dirs(cfg):
    """
    Create the directories needed for the package index reflected by *pkg*
    """
    root = local(cfg['root'])
    root.ensure_dir()
    for pkg in cfg['pkglist']:
        root.ensure_dir(pkg)


# -----------------------------------------------------------------------------
def conditional_debug(debug_option):
    """
    Start the debugger if the debug option is True
    """
    if debug_option:
        pdb.set_trace()


# -----------------------------------------------------------------------------
def read_cfg_file(filename):
    """
    Load config data from *filename*
    """
    rval = {'root': None,
            'pkglist': {}}
    with open(filename, 'r') as rbl:
        cpkg = None
        for line in rbl:
            # throw away any comment at the end of the line
            # the '#' must be followed by whitespace to be a valid comment
            line = re.sub(r"\s*#\s.*$", "", line)
            # ignore blank lines
            if re.match(r"^\s*$", line):
                continue
            (key, val) = line.split()
            key = key.strip()
            val = val.strip()
            if key == 'root':
                if rval['root'] is None:
                    rval['root'] = tbx.expand(val)
                else:
                    raise pyppi_error("root was already set")
            elif key == 'package':
                rval['pkglist'][val] = []
                cpkg = rval['pkglist'][val]
            elif key == 'version':
                cpkg.append({'version': val})
            elif key == 'url':
                cpkg[-1]['url'] = val
            elif key == 'minpy':
                cpkg[-1]['minpy'] = val
    return rval


# -----------------------------------------------------------------------------
class pyppi_error(Exception):
    """
    Error class for errors in this program
    """
    pass


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    dispatch(__doc__)

# ==TAGGABLE==
