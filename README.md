cpd - Change to Project Directory
=================================

Platform Support
----------------

This supports Unix systems with Python 2.x or Python 3.x available. It
has yet to be tested on Windows (`cmd`, PowerShell and MinGW Bash)
systems.


Usage
-----

`cpd` is configured with a list of _target paths_, usually including
shell glob patterns, read from `~/.config/cpd/project-paths`. On the
command line it is given a space-separated set of _target path
components_ and, optionally, a space- or slash-separated list of
_subpath components_, the first one of which must start with a slash
to separate it from the target path components. All components (both
target path and subpath) may include glob patterns and all components
have an implicit `*` appended to become prefix globs.

From the set of target path components it finds target paths that
match all of those components, in any order. Thus, set `{de, b}`
(expressed as `de b`  or `b de` on the command line) would match
target path `/alpha/bravo/charlie/delta` because `de*` matches the
`delta` component and `b*` matches the `bravo` component.

Once target paths have been selected, a second search is done for
paths below these target paths that are directories that match, in
order, the list of subpath components. Thus, list `gh j` or `gh/j`
would match a target path that has below it a directory `/ghi/jkl/`,
but not a target path that has below it only a directory `/jkl/ghi/`
nor a target path that has below it only a file `/ghi/jkl`.

This produces a final list of matching target paths each of which has
at least one matching subpath. This is ordered first by the rightmost
matching components in the target path portion; that is, given target
path components `{f}`, `/bar/foo` will be considered a better match
than `/foo/bar`. Within that order, subpath components are ordered
lexicographically.

If the `-l` option is given to `cpd` these paths will be listed in
order, otherwise the current working directory will be changed to
the first path in the list.

#### Target Path Examples

If your `project-paths` contains:

    ~/co/*/*/*
    ~/golang/src/*/*/*

And this expands to the following target paths on your disk:

    ~/co/freedesktop.org/xdg/xdg-user-dirs
    ~/co/github.com/0cjs/git-tools
    ~/co/github.com/dot-home/_dot-home
    ~/co/github.com/dot-home/git-tools
    ~/golang/src/github.com/golang/go
    ~/golang/src/github.com/libgit2/git2go
    ~/golang/src/github.com/graphviz/dotty

Here are some sample `cpd` commands and their effects:

* `cpd xdg`  
  `~/co/freedesktop.org/xdg/xdg-user-dirs`  
  because it's the only target path with any component matching glob `xdg*`.
* `cpd *tools`  
  `~/co/github.com/0cjs/git-tools`  
  because it's lexically first of the two target paths with components
  matching `*tools`.
* `cpd *tools dot`  
  `~/co/github.com/dot-home/git-tools`  
  because it's the only target path matching both `*tools` and `dot*`.
* `cpd dot`  
  `~/golang/src/github.com/graphviz/dotty`  
  because 'dotty' is a rightmost component matching `dot*`.
  `dot-home/_dot-home` and `dot-home/tools` are both lexically earlier
  matches, but they match in the second-right component and thus are
  lower priority.

#### Subpath Examples

Given the following combinations of target path (from `project-paths`)
and subpath (from the filesystem), separated by spaces for clarity:

    ~/co/github.com/0cjs/proj1          /lib/foo/util
    ~/co/github.com/0cjs/proj1          /lib/bar/util
    ~/co/github.com/nishantjr/proj2     /lib/proj2
    ~/co/github.com/nishantjr/proj2     /data/foo/bar

Here are samples of `cpd` commands and their effects:

* `cpd p /d`  
  `~/co/github.com/nishantjr/proj2/data`  
  Only `proj2` has a subdirectory matching `d*`.
* `cpd p /l`  
  `~/co/github.com/0cjs/proj1/lib`  
  Both target paths match and have a matching subpath; `0cjs` has priority.
* `cpd p /l f u`  
  `~/co/github.com/0cjs/proj1/lib/foo/util`
  Subpath components may be separated by spaces, as with target path components.
* `cpd p /l/f/u`  
  `~/co/github.com/0cjs/proj1/lib/foo/util`
  Subpath components also may be separated by slashes instead.
* `cpd p /l//u`  
  `~/co/github.com/0cjs/proj1/lib/foo/util`  
  Subpath components may be empty, becoming just `*`.
* `cpd /**/util`  
  `~/co/github.com/0cjs/proj1/lib/foo/util`  
  'Recursive' globs matching any number of components are allowed.
  When a list of subpath globs is given, the set of target path
  globs may be empty.


Installation
------------

#### By Hand

Copy the `bin/cpd.py` file in to your path and change your `~/.bashrc`
to include the functions and `complete` setup from `dot/bashrc.inb4`.

#### As a [dot-home] Module

    mkdir -p ~/.home
    cd ~/.home
    git clone https://github.com/dot-home/_dot-home.git     # Core system
    git clone https://github.com/dot-home/cpd.git     # This repo
    ~/.home/_dot-home/bin/dot-home-setup


Testing and Development
-----------------------

This is an example of a [dot-home] module containing an application
that resides entirely in a single file (in this case, `bin/cpd.py`)
with no supporting libraries required beyond the standard library that
comes with the application's language.

The test framework requires the `virtualenv` Python package in order
to set up the rest of the test environment. Normally we install this
using `pip install --user virtualenv` after installing `pip` via
either OS packages or by hand.

The important development files and directories are:

* `Test` uses `activate` to set up and activate the virtual
  environment and then runs the unit and functional test suites.
* `activate`, when sourced in a Bash shell (`. activate`), will
  set up the virtual environment if necessary and change your command
  line environment to use it. You can then run the code and tests from
  the command line.
* `requirements.txt` contains the list of Python packages used by the
  test framework. (None of these are required by the script itself.)
* `t/` contains test data.
* `.build/` contains the virtualenv created by `activate` and any
  other build products. Remove this for a clean build.

#### Build/Test Arguments

`Test` will reuse any existing Python virtualenv under `.build/`
unless given `-C` as the _first_ option, which wipes out the entire
`.build/` directory to do a clean build.

Any additional options will be passed on to `pytest` (between the
options and the list of files containing tests). This is typically
used to change verbosity and run test subsets, e.g.

    ./Test -v -v -k flat

#### Python Versions

This is designed to run under both Python 2 and 3. The `Test` script
builds a Python 2 virtualenv by default, but you can remove `.build/`
and source `activate` by hand to use whatever version of Python you
like:

    . activate -p python3       # Force use of Python 3
    . activate                  # Use virtualenv's default Python version


Authors
-------

* Curt J. Sampson <cjs@cynic.net> github:[0cjs]
* Nishant Rodrigues <nishantjr@gmail.com> github:[nishantjr]



[dot-home]: https://github.com/dot-home/_dot-home
[nishantjr]: https://github.com/nishantjr
[0cjs]: https://github.com/0cjs
