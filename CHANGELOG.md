## 0.0.3 ... 2019-11-28 21:12:12

 * Fixed issues with cpush

## 0.0.2 ... 2019-11-28 16:48:07

 * Set 3.6.9 as the minimum supported python version
 * Arrange to call pyppi directly as an executable, not invoking a module with
   the python executable
 * We need to catch colons if they are in the config file separating keys and
   values -- added test and payload for this.
 * Add function cpush: if any of the pypi index.html files are out of date with
   respect to the config file, rebuild. Then stage any outstanding index.html
   files, git commit them, and git push to update the active index up at github.


## 0.0.1 ... 2019-11-27 16:01:20

 * Project inception
 * Ability to read a config file describing the desired package index
 * Make all source files "taggable" so 'make tags' will see them
 * Create package index directories based on the config file
 * Added documentation to __init__.py so 'pydoc pyppi' makes it visible
 * Tests for config file reading, 'pyppi version', code quality, and ensure
   that all functions have a non-empty __doc__ string
 * Test and payload for cmkdir() was added but then removed when we moved
   to using py.path.local
 * Tests for the output of 'pydoc pyppi', 'pyppi help', and 'pyppi --help'
 * Update setup.py so that the command line entry point is available in
   $PATH and 'alias pyppi=python pyppi' is no longer needed
 * Distribute LICENSE, README.md, CHANGELOG.md at installation time
 * Test to verify that all test functions call pytest.dbgfunc()
 * Test for deployability
 * Applying the unlicense (see <unlicense.org>)
