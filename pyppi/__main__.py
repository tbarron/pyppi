"""
USAGE:
    pyppi build [-d] FILENAME
    pyppi version [-d]

DESCRIPTION
    pyppi build [-d] FILENAME
        Build the python package index based on the contents of FILENAME.

    pyppi version [-d]
        Report the pyppi version.

This is free and unencumbered software released into the public domain.
For more information, please visit <http://unlicense.org/>.
"""
from docopt_dispatch import dispatch
import pdb
from pyppi import version
from py.path import local
import re
import tbx


# -----------------------------------------------------------------------------
def main():
    """
    Main entry point
    """
    dispatch(__doc__)


# -----------------------------------------------------------------------------
@dispatch.on('build')
def pyppi_build(**kw):                                       # pragma: no cover
    """
    Build the package index from kw['FILENAME']
    """
    conditional_debug(kw['d'])
    filename = kw['FILENAME']
    print("Reading config file {}".format(filename))
    cfg = read_cfg_file(filename)
    build_dirs(cfg)
    build_index_htmls(cfg)


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
    for pkg in cfg['packages']:
        root.ensure_dir(pkg)


# -----------------------------------------------------------------------------
def build_index_htmls(cfg):
    """
    Write an index.html file for root and for each package
    """
    index_html_root(cfg)
    pkg_d = cfg['packages']
    for pkg in pkg_d:
        index_html_package(cfg['root'], pkg, pkg_d[pkg])


# -----------------------------------------------------------------------------
def index_html_root(cfg):
    """
    Write the root package index.html
    """
    root = local(cfg['root'])
    target = root.join("index.html")
    print("writing file {}".format(target.strpath))
    payload = ("<!DOCTYPE html>\n"
               "<html>\n"
               "  <body>\n")
    pkg_l = cfg['packages']
    for pkg in pkg_l:
        payload += "    <a href=\"/{}/{}/\">{}</a>\n".format(cfg['root'],
                                                             pkg,
                                                             pkg)
    payload += ("  </body>\n"
                "</html>\n")
    target.write(payload)


# -----------------------------------------------------------------------------
def index_html_package(root, pkgname, pkg_l):
    """
    Write an index.html for each package in cfg
    """
    target = local("{}/{}/index.html".format(root, pkgname))
    print("writing file {}".format(target.strpath))
    payload = ("<!DOCTYPE html>\n"
               "<html>\n"
               "  <body>\n")
    for release in pkg_l:
        payload += "    <a href=\"{}\"".format(release['url'])
        if 'minpy' in release:
            payload += " {}=\"&gt;={}\"".format("data-requires-python",
                                                release['minpy'])
        payload += ">{}-{}</a>\n".format(pkgname, release['version'])
    payload += ("  </body>\n"
                "</html>\n")
    target.write(payload)


# -----------------------------------------------------------------------------
def conditional_debug(debug_option):                         # pragma: no cover
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
            'packages': {}}
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
                rval['packages'][val] = []
                cpkg = rval['packages'][val]
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

# ==TAGGABLE==
