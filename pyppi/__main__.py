"""
USAGE:
    pyppi build [-d] FILENAME
    pyppi cpush [-d] -m MESSAGE FILENAME
    pyppi version [-d]

OPTIONS:
    -m MESSAGE      Specify MESSAGE for git commit

DESCRIPTION
    pyppi build [-d] FILENAME
        Build the python package index based on the contents of FILENAME.

    pyppi cpush [-d] -m MESSAGE FILENAME
        if mtime(root/*/index.html) < mtime(FILENAME):
            build
        if any files staged,
            complain and die
        if none of root/*/index.html pending:
            complain and die
        git add root/*/index.html
        git commit -m MESSAGE
        git push

    pyppi version [-d]
        Report the pyppi version.

This is free and unencumbered software released into the public domain.
For more information, please visit <http://unlicense.org/>.
"""
from docopt_dispatch import dispatch
import pdb
from pyppi import version
from py.path import local as pypath
import re
import shutil
import sys
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
@dispatch.on('cpush')
def pyppi_cpush(**kw):
    """
    if mtime(root/*/index.html) < mtime(FILENAME):
        build
    if any non pypi files staged,
        complain and die
    if none of root/*/index.html pending:
        complain and die
    git add root/*/index.html
    git commit -m MESSAGE
    git push
    """
    conditional_debug(kw['d'])
    filename = kw['FILENAME']
    cfg = read_cfg_file(filename)
    if index_out_of_date(filename, cfg):
        shutil.rmtree(cfg['root'])
        build_dirs(cfg)
        build_index_htmls(cfg)

    root = cfg['root']
    (untracked, unstaged, uncommitted) = tbx.git_status()
    others = [_ for _ in uncommitted
              if root not in _ or 'index.html' not in _]
    if others:
        sys.exit("You have files staged. Please commit them and try again.")

    taddables = [_ for _ in untracked if root in _ and 'index.html' in _]
    saddables = [_ for _ in unstaged if root in _ and 'index.html' in _]
    addables = taddables + saddables
    if len(addables) == 0:
        sys.exit("No pypi index.html files are unstaged")
    else:
        git_add(addables)

    git_commit(message=kw['m'])
    git_push()


# -----------------------------------------------------------------------------
def index_out_of_date(filename, cfg):
    """
    Return True if mtime(filename) is later than mtime(any index.html under
    root)
    """
    rval = False
    cfgfile = pypath(filename)
    root = cfg['root']
    idxhtml_l = [pypath("{}/index.html".format(root))]
    pkg_d = cfg['packages']
    for pkg in pkg_d:
        path = "{}/{}/index.html".format(root, pkg)
        idxhtml_l.append(pypath(path))

    for idxh in idxhtml_l:
        if not idxh.exists():
            rval = True
            break
        elif idxh.mtime() < cfgfile.mtime():
            rval = True
            break

    return rval


# -----------------------------------------------------------------------------
def git_add(addables):
    """
    Run 'git add' on the group of paths in *addables*
    """
    addable_list = " ".join(addables)
    cmd = "git add {}".format(addable_list)
    tbx.run(cmd)


# -----------------------------------------------------------------------------
def git_commit(message=""):
    """
    Run 'git commit' with *message*
    """
    cmd = "git commit -m \"{}\"".format(message)
    tbx.run(cmd)


# -----------------------------------------------------------------------------
def git_push():
    """
    Run 'git push'
    """
    tbx.run("git push")


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
    root = pypath(cfg['root'])
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
    root = pypath(cfg['root'])
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
    target = pypath("{}/{}/index.html".format(root, pkgname))
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
            if ':' in key:
                msg = "Syntax error in config file: colons not allowed"
                raise pyppi_error(msg)
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
