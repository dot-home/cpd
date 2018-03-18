#!/usr/bin/env python

from argparse import ArgumentParser
from fnmatch import fnmatch
from functools import reduce
from glob import glob
from os import environ
from os.path import expanduser, split as pathsplit
import sys

project_path_globs_file = '~/.config/cpd/project-paths'

def flatten(xs):
    return sum(xs, [])     # Monads are handy!
                           # https://stackoverflow.com/a/952946/107294

def readconfig():
    with open(expanduser(project_path_globs_file), 'r') as f:
        return map(str.strip, f.readlines())

def expand_pdglob(pdglob):
    ''' Expand the glob pattern to a list of filesystem paths that are
        directories that match the glob. `~` expansion is performed.
    '''
    return glob(expanduser(pdglob))

def pdmatches(component_globs):     # !!! Curried
    ''' Return a function that will return all paths from `project_paths`
        that have components matching all `component_globs`. Each
        component_glob has an implied `*` at the end.
    '''
    return(lambda project_paths:
        filter(
            lambda path:
                all(glob_match(path, glob) for glob in component_globs),
            project_paths))

def glob_match(path, glob):
    return any(fnmatch(component, glob + '*')
               for component in pathcomponents(path))

def pathcomponents(path):
    prefix, component = pathsplit(path)
    if prefix not in ['', '/']:         # Fixed point
        return pathcomponents(prefix) + [component]
    else:
        return [component]

def main():
    parser = ArgumentParser(description='''
        Find project directories by matching glob patterns to path components.

        A list of path glob patterns, one per line, is read from `%s`.
        (`~` is interpreted as your home dir.) Each path in the
        filesystem matching matching any of these globs is considered
        a project path.

        A set of component globs is given on the command line, and
        each project path matching all component globs is printed.

        ''' % project_path_globs_file)
    parser.add_argument('--complete-words', action='store_true', help='''
        Return list of matching project paths separated by null char.
        (Use `read -d $'\\0' to read these.)
        ''')
    parser.add_argument('component_glob', nargs='*',
        help='glob patterns to match components in paths')
    args = parser.parse_args()

    separator = '\n'
    if args.complete_words: separator = '\0'
    pathss = map(expand_pdglob, readconfig())
    for match in flatten(map(pdmatches(args.component_glob), pathss)):
        sys.stdout.write(match)
        sys.stdout.write(separator)

if __name__ == '__main__':
    main()
