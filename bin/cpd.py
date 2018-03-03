#!/usr/bin/env python

import sys
from argparse import ArgumentParser

project_path_globs_file = '~/.config/cpd/path-globs'

def test_nothing():
    assert True

def pdmatches(component_globs):
    return []

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
    for match in pdmatches(args.component_glob):
        sys.stdout.write(match)
        sys.stdout.write(separator)

if __name__ == '__main__':
    main()
    pass
