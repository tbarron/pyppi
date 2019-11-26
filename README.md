# pyppi - Build a python package index

This package takes a config file in the following format and turns it into
a python package index that conforms to PEP 503 (Simple Repository API).

    PACKAGE
        version: X.Y.Z
        url:     git+https://github.com/tbarron/PKG#egg=PKG-X.Y.Z
        minpy:   A.B.C
        version: ...
        ...
    PACKAGE

  * Each PACKAGE may have zero or more versions, but a package with no versions
    will not generate an entry in the index.

  * The URL in the format above is an example. Per the PEP, there is no
    constraint on the location of the files relative to the index.

  * The minpy entry is optional and may be omitted. If present, it will
    generate a "data-requires-python" attribute on the anchor for the
    release.
