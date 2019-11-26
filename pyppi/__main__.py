"""
Usage:
    pyppi build [-d] FILENAME
"""
from docopt_dispatch import dispatch
import pdb
from pprint import pprint
import re


# -----------------------------------------------------------------------------
@dispatch.on('build')
def pyppi_build(**kw):
    """
    Build the package index from kw['FILENAME']
    """
    if kw['d']:
        pdb.set_trace()
    filename = kw['FILENAME']
    print("Read config file {}".format(filename))
    cfg = read_cfg_file(filename)
    pprint(cfg)


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
                    rval['root'] = val
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
    pass


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    dispatch(__doc__)

# ==TAGGABLE==
