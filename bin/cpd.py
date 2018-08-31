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

def span(p, seq):
    ''' Return a tuple where the first element is the longest prefix of
        `seq` satisfying predicate `p` and the second element is the rest.
    '''
    i = 0
    for i, x in enumerate(seq):
        if not p(x):
            break
        i = i+1     # for when we reach end
    return (seq[0:i], seq[i:])

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

def pathcomp_prefixglob(path):
    ''' Given a `/`-separated path, add a trailing `*` to each path
        component that doesn't already have one.
    '''
    if path is None:
        return None
    if path.startswith('/'):    prefix = '/'    # Seems like a hack!
    else:                       prefix = ''
    def starsuffix(s):
        if s.endswith('*'):     return s
        else:                   return s + '*'
    return prefix + '/'.join(map(starsuffix, pathcomponents(path)))

@total_ordering
class MatchingPath():
    ''' A path that sorts in 'best match' order. '''

    class AllGlobsMustMatch(RuntimeError):      pass
    class Incomparable(RuntimeError):           pass

    @staticmethod
    def constructor(tp_component_globs, subpath_glob):
        ''' Return a constructor function ``c(path) -> MatchingPath | None``
            that builds `MatchingPath` objects or `None` if not all globs
            match.  See `__init__()` below for details of the arguments.
        '''
        def cons(path):
            try:
                return MatchingPath(path,
                    tp_component_globs, pathcomp_prefixglob(subpath_glob))
            except MatchingPath.AllGlobsMustMatch:
                return None
        return cons

    def __init__(self, path, tp_component_globs, subpath_glob):
        ''' path (str):
                The path against which to match the globs
            tp_component_globs (collection, order ignored):
                A collection of glob patterns (``*`` implicitly appended),
                all of which must match against any component (in any
                order) of the target path.
            subpath_glob (`str` or `None`):
                A glob pattern matching all components of a path
                underneath the target path, e.g., ``a*/**/b*``, or
                `None` if no subpath match should be done.
        '''
        self.path = path
        self.cglobs = set(tp_component_globs)
        self.subpath_glob = subpath_glob
        self.sortkey = self.makesortkey(tp_component_globs)(path)

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

def split_arg_globs(globs):
    ''' The arguments are a list of globs, the target path components
        followed by the subpath components. Separate these  and return
        a tuple of:
        * a `set` of target path components, and
        * a subpath of:
          - `None` if no subpath was given, or
          - a single `str` with internal slashes separating the
            subpath components
    '''
    prefix, suffix = span(lambda x: x[0] != '/', globs)
    suffix = '/'.join(suffix)
    if suffix == '': suffix = None
    return prefix, suffix

def matchandsort(component_globs, target_paths):
    ''' Taking a list of component_globs (each with implied `*` at end)
        and list of target_paths, return a sorted list of MatchingPaths.
    '''
    targetpath_globs, subpath_glob = split_arg_globs(component_globs)
    mpcons = MatchingPath.constructor(targetpath_globs, subpath_glob)
    def notNone(x): return x is not None
    return sorted(filter(notNone, map(mpcons, target_paths)))

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
