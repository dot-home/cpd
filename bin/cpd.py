#!/usr/bin/env python

from argparse import ArgumentParser
from fnmatch import fnmatch
from functools import reduce, total_ordering
from glob import glob
from os import environ
from os.path import expanduser, split as pathsplit
import sys

target_globs_file = '~/.config/cpd/project-paths'

def flatten(xs):
    #   Monads are handy!  https://stackoverflow.com/a/952946/107294
    return sum(map(list, xs), [])

def reverse(s):
    return s[::-1]

def readconfig():
    with open(expanduser(target_globs_file), 'r') as f:
        return map(str.strip, f.readlines())

def expand_target_glob(target_glob):
    ''' Expand the glob pattern to a list of filesystem paths that are
        directories that match the glob. `~` expansion is performed.
    '''
    return glob(expanduser(target_glob))

def pathcomponents(path):
    ''' Given a path of '/'-separated components, return the components.
        This excludes empty components excepting one at the end if the
        path ends with '/'.
    '''
    prefix, component = pathsplit(path)
    if prefix not in ['', '/']:         # Fixed point
        return pathcomponents(prefix) + [component]
    else:
        return [component]

@total_ordering
class MatchingPath():
    ''' A path that sorts in 'best match' order. '''

    class AllGlobsMustMatch(RuntimeError):      pass
    class Incomparable(RuntimeError):           pass

    @staticmethod
    def constructor(component_globs):
        ''' Return a constructor function that builds MatchingPath
            objects. The constructor takes and returns a MatchingPath
            if all `component_globs` globs match at least one path
            component, or `None` otherwise.
        '''
        def cons(path):
            try:
                return MatchingPath(path, component_globs)
            except MatchingPath.AllGlobsMustMatch:
                return None
        return cons

    def __init__(self, path, component_globs, subpath_glob):
        ''' Parameters:
            path:
                XXX
            component_globs:
                XXX
            subpath_glob:
                A single glob pattern matching all components of the
                subpath, e.g., ``a*/**/b*``.
        '''
        self.path = path
        self.cglobs = set(component_globs)
        self.subpath_glob = subpath_glob
        self.sortkey = self.makesortkey(component_globs)(path)

    @staticmethod
    def makesortkey(component_globs):
        ''' Take list of component_globs and (curried) path string and return
            a tuple of the path and the match data. If every glob matched at
            least one component, the match data is a string of `0` and `1`
            indicating which components matched any glob. If not all globs
            matched a component, `None` is returned.
        '''
        def concat(strs): return ''.join(strs)
        def f(path):
            def matches_glob(component):
                for glob in component_globs:
                    if fnmatch(component, glob + '*'):
                        return glob
                return None
            #   Convert globs_and_nones to a list now because we use it
            #   several times and otherwise we'd need to reset the iterator.
            globs_and_nones = list(map(matches_glob, pathcomponents(path)))
            matched_globs = set(globs_and_nones) - set([None])
            if matched_globs != set(component_globs):
                raise MatchingPath.AllGlobsMustMatch()
                return None # Not all matched
            sortkey = reverse(concat(
                map(lambda x: '+' if x else '_', globs_and_nones)))
                #   Match ('+', 43) sorts before non-match('_', 95)
            return sortkey
        return f

    def assertComparable(self, other):
        if self.cglobs != other.cglobs:
            raise self.Incomparable('different component_globs')

    def __eq__(self, other):
        self.assertComparable(other)
        return self.path == other.path

    def __lt__(self, other):
        self.assertComparable(other)
        return (self.sortkey, self.path) < (other.sortkey, other.path)


def matchandsort(component_globs, target_paths):
    ''' Taking a list of component_globs (each with implied `*` at end)
        and list of target_paths, return a sorted list of MatchingPaths.
    '''
    def notNone(x): return x is not None
    return sorted(filter(notNone,
            map(MatchingPath.constructor(component_globs), target_paths)))

def main():
    parser = ArgumentParser(description='''
        Find project directories by matching glob patterns to path components.

        A list of target path glob patterns, one per line, is read
        from `%s`. (`~` is interpreted as your home dir.) Each path in
        the filesystem matching matching any of these globs is
        considered a target path.

        A set of component globs is given on the command line, and
        each target path matching all component globs is printed.

        ''' % target_globs_file)
    parser.add_argument('--complete-words', action='store_true', help='''
        Return list of matching target paths separated by null char.
        (Use `read -d $'\\0' to read these.)
        ''')
    parser.add_argument('component_globs', nargs='*',
        help='glob patterns to match components in paths')
    args = parser.parse_args()

    separator = '\n'
    if args.complete_words: separator = '\0'
    target_paths = flatten(map(expand_target_glob, readconfig()))
    for match in matchandsort(args.component_globs, target_paths):
        sys.stdout.write(match.path)
        sys.stdout.write(separator)

if __name__ == '__main__':
    main()
