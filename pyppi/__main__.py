"""
Usage:
    pyppi build [-d] FILENAME
"""
from docopt_dispatch import dispatch


@dispatch.on('build')
def pyppi_build(**kw):
    """
    """
    if kw['d']:
        pdb.set_trace()
    print("hello world!")


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    dispatch(__doc__)
