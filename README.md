cpd - Change to Project Directory
=================================

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

### By Hand

Copy the `bin/cpd.py` file in to your path and change your `~/.bashrc`
to include the functions and `complete` setup from `dot/bashrc.inb4`.

### As a [dot-home] Module

    mkdir -p ~/.home
    cd ~/.home
    git clone https://github.com/dot-home/_dot-home.git     # Core system
    git clone https://github.com/dot-home/cpd.git     # This repo
    ~/.home/_dot-home/bin/dot-home-setup


[dot-home]: https://github.com/dot-home/_dot-home
