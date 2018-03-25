cpd - Change to Project Directory
=================================

Platform Support
----------------

This supports Unix systems with Python 2.x or Python 3.x available. It
has yet to be tested on Windows (`cmd`, PowerShell and MinGW Bash)
systems.


Usage
-----

This reads a list of paths (which usually include shell glob patterns)
from `~/.config/cpd/project-paths` and changes the current working
directory to the first path that has components matching glob patterns
(with an implied `*` at the end) given on the command line.

For example, if your `project-paths` contains:

    ~/co/*/*/*
    ~/golang/src/*/*/*

And this expands to the following project directories:

    ~/co/freedesktop.org/xdg/xdg-user-dirs
    ~/co/github.com/0cjs/git-tools
    ~/co/github.com/dot-home/_dot-home
    ~/co/github.com/dot-home/git-tools
    ~/golang/src/github.com/golang/go
    ~/golang/src/github.com/libgit2/git2go

The following `cpd` commands will change to:

    $ cpd xdg           #  ~/co/freedesktop.org/xdg/xdg-user-dirs
    $ cpd *tools        #  ~/co/github.com/0cjs/git-tools
    $ cpd *tools dot    #  ~/co/github.com/dot-home/git-tools


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
