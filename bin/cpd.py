#!/usr/bin/env python

from argparse import ArgumentParser
from fnmatch import fnmatch
from functools import reduce
from glob import glob
from os import environ
from os.path import expanduser, split as pathsplit
import sys

project_path_globs_file = '~/.config/cpd/project-paths'

def readconfig():
    with open(expanduser(project_path_globs_file), 'r') as f:
        return map(str.strip, f.readlines())

def expand_pdglobs(pdglobs):
    ''' Expand the list of globs to a list of filesystem paths that are
        directories that match the globs. `~` expansion is performed.
    '''
    return reduce(lambda x, y: x + y, map(glob, map(expanduser, pdglobs)))

def test_pdmatches():
    p1  = '/projects/one'
    p3  = '/projects/three'
    hp1 = '/home/foo/projects/one'
    hp2 = '/home/foo/projects/two'
    pps = [ p1, p3, hp1, hp2 ]
    assert pdmatches(pps, ['no-match']) == []
    assert pdmatches(pps, ['on'])       == [ p1, hp1 ]
    assert pdmatches(pps, ['ho'])       == [ hp1, hp2 ]
    assert pdmatches(pps, ['on', 'ho']) == [ hp1 ]
    assert pdmatches(pps, ['on', 'tw']) == [ ]

def pdmatches(project_paths, component_globs):
    ''' Return all paths from `project_paths` that have components
        matching all `component_globs`. Each component_glob has an
        implied `*` at the end.
    '''
    return filter(
        lambda path:
            all(glob_match(path, glob) for glob in component_globs),
        project_paths)

def test_glob_match():
    path = '/foo/bar/baz/quux'  # No 'g's in here!
    matches = [ '', '*',
        'foo', 'f',
        'b', 'bar', 'b*', 'bar*',
        'quu', '*quu',
        '?a', '[abc]a',
        ]
    non_matches = [
        'g', '*g', 'x*', 'quuxz*', '?b', '[ac]a',
        '/', # We don't currently support matches across multiple components.
        ]
    for m in matches:
        assert glob_match(path, m)
    for n in non_matches:
        assert not glob_match(path, n)

def glob_match(path, glob):
    return any(fnmatch(component, glob + '*')
               for component in pathcomponents(path))

def test_pathcomponents():
    p = pathcomponents
    assert p('')                == ['']
    assert p('/')               == ['']
    assert p('foo')             == ['foo']
    assert p('foo')             == ['foo']
    assert p('/foo')            == ['foo']
    assert p('foo/')            == ['foo', '']
    assert p('/foo/')           == ['foo', '']
    assert p('foo/bar')         == ['foo', 'bar']
    assert p('/foo/bar')        == ['foo', 'bar']
    assert p('foo/bar/')        == ['foo', 'bar', '']
    assert p('/foo/bar/')       == ['foo', 'bar', '']
    assert p('/foo///bar/')     == ['foo', 'bar', '']
    assert p('/a/b/c/d/e')      == ['a', 'b', 'c', 'd', 'e']

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
    for match in pdmatches(expand_pdglobs(readconfig()), args.component_glob):
        sys.stdout.write(match)
        sys.stdout.write(separator)

if __name__ == '__main__':
    main()
