import pytest

from cpd import *


def test_flatten():
    assert ['a', 1, 'b', 2] == flatten([['a', 1], ['b', 2]])

def test_reverse():
    assert    [3,2,1] == reverse([1,2,3])

def test_span():
    seq = (0, 1, 2, 3)
    def lt(n): return lambda x: x < n
    assert ((0,1), (2,3))   == span(lt(2), seq)
    assert ((0,), (1,2,3))  == span(lt(1), seq)
    assert ((), (0,1,2,3))  == span(lt(0), seq)
    assert ((0,1,2,3), ())  == span(lt(4), seq)

    #   We return the sequence type we were given
    assert ([0,1], [2, 3])  == span(lt(2), [0, 1, 2, 3])

    #   Works with empty sequences
    assert ([], [])         == span(lt(0), [])

    #   Works with string values in sequences
    def notstartslash(s): return s[0] != '/'
    assert (['a','b'], ['/c','d']) == span(notstartslash, ['a', 'b', '/c', 'd'])
    assert (['a','b', 'c'], [])    == span(notstartslash, ['a', 'b', 'c'])

def test_expand_target_glob():
    #   This relies on CWD being set to the dir above `t/`
    #   and $HOME being set to `t/home` in this project.
    assert 't/home/p1/abc' in expand_target_glob('t/home/*/*')
    assert expand_target_glob('~/p?')[1][-9:] == 't/home/p2'

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

@pytest.mark.parametrize('input, expected', (
    (None,      None),
    ('/a/b',    '/a*/b*'),
    ('/a*/b',   '/a*/b*'),
    ('/a*/b*',  '/a*/b*'),
    ('/',       '/*'),
    ('/a/',     '/a*/*'),
    #   XXX These tests fail because prefixglob_pathcomponents() uses
    #   pathcomponents(); the latter drops empty components `//`, which
    #   is wrong for this particular application. It's not clear why
    #   pathcomponents() does that; it looks like that may not be necessary.
    #('//',      '/*/*'),
    #('//t',     '/*/*/t'),
    ))
def test_prefixglob_pathcomponents(input, expected):
    assert expected == prefixglob_pathcomponents(input)

@pytest.mark.parametrize('globs, path, rkey', [
    #   Sort key is '+' for match, '_' for not, reversed
    (['a'       ],  '/charlie/bravo/alpha',     '+__'),
    (['a'       ],  '/alpha/bravo/alpha',       '+_+'),
    (['b'       ],  '/bravo/bravo/bravo',       '+++'),
    (['a', 'b'  ],  '/bravo/alpha/charlie',     '_++'),
    (['a'       ],  '/foo/bravo/alpha',         '+__'),
    (['b'       ],  '/bravo/bravo/bravo',       '+++'),
    (['a', 'b'  ],  '/bravo/alpha/charlie',     '_++'),

    pytest.param(['a', 'al' ], '/bravo/alpha/charlie', '_+_',
        marks=pytest.mark.xfail(strict=True, reason='bug: both globs match'
            ' but we return just the first glob that matched, internally')),

    #   Glob testing
    (['',       ],  '/alpha/bravo/charlie',     '___'), # XXX no matches?
    (['?r',     ],  '/alpha/bravo/charlie',     '_+_'),
    (['??a',    ],  '/alpha/bravo/charlie',     '++_'),
    (['a*p',    ],  '/alpha/bravo/charlie',     '__+'),
    (['[ab]',   ],  '/alpha/bravo/charlie',     '_++'),
    (['[ac]',   ],  '/alpha/bravo/charlie',     '+_+'),
    (['*[xyz]'  ],  '/nope/yes/aaaz/abxcd',     '+++_'),
])
def test_makesortkey(globs, path, rkey):
    assert (rkey, path) == (MTP.makesortkey(globs)(path), path)

def test_makesortkey_notallmatch():
    inputs = [
        (['x', 'b'],    '/bravo/alpha/charlie'),
        (['a'],         '/bravo/bravo/bravo'),
        (['a*b'],       '/alpha/bravo'),
    ]
    for globs, path in inputs:
        with pytest.raises(MTP.AllGlobsMustMatch):
            MTP.makesortkey(globs)(path)

def mp(path):
    ''' Our standard test MTP with a fixed glob.
        Has no subpath glob; that's tested separately.
        Matching:     bravo, delta
        Non-matching: alpha, charlie, echo
    '''
    return MTP(path, ['b', 'd'], None)

def test_MTP_construction():
    ''' An MTP must always have at least one component matching
        each glob. This is an integration test; the full test of the
        check is test_MTP_makesortkey_notallmatch.
    '''
    assert mp('/charlie/bravo/delta')
    with pytest.raises(MTP.AllGlobsMustMatch):
        assert mp('/charlie/bravo/echo')

def test_MTP_ordering():
    #   XXX This test assumes that all component_globs match a component!

    with pytest.raises(MTP.Incomparable):
        mp('/bravo/delta') == MTP('/bravo/delta', ['b', 'de'], None)
    with pytest.raises(MTP.Incomparable):
        mp('/bravo/delta') < MTP('/bravo/delta', ['b', 'de'], None)

    assert mp('/bravo/delta') == mp('/bravo/delta')
    assert mp('/bravo/delta') != mp('/bravo/delta/charlie')

    #   If the indices of the matching components are the same for
    #   both, use lexical order.
    assert mp('/bravo/delta')       < mp('/delta/bravo')
    assert mp('/alpha/bravo/delta') < mp('/echo/bravo/delta')
    assert mp('/echo/bravo/delta')  < mp('/echo/delta/bravo')

    #   If matching component is more to the right, that path sorts first.
    #   I.e., We want to sort matches deeper in the path before those
    #   closer to the beginning because we're thinking first about our
    #   project names and then about how the projects are grouped at
    #   higher level.
    assert mp('/echo/bravo/delta')          < mp('/bravo/delta/echo')
    assert mp('/echo/bravo/delta/foxtrot')  < mp('/bravo/delta/echo/foxtrot')
    assert mp('/echo/bravo/delta')          < mp('/bravo/delta/echo/foxtrot')
    assert mp('/echo/bravo/delta')          < mp('/alpha/bravo/delta/foxtrot')
    assert mp('/alpha/foxtrot/bravo/delta') < mp('/bravo/delta/echo')
    assert mp('/bravo/bravo/delta')         < mp('/bravo/echo/bravo/delta')

def test_MTP_constructor_nosubpathglobs():
    def m(tpglobs): return MTP.constructor(tpglobs, None)
    assert     m(['a'       ])('/foo/bravo/alpha')
    assert not m(['a'       ])('/bravo/bravo/bravo')
    assert     m(['b'       ])('/bravo/bravo/bravo')
    assert     m(['a', 'b'  ])('/bravo/alpha/charlie')
    assert not m(['x', 'b'  ])('/bravo/alpha/charlie')

@pytest.mark.xfail(
    reason='Subpath globs can be tested only against a real filesystem')
#   Because of our use of glob() we can test only against real paths
#   in a filesystem. glob() just uses listdir() and fnmatch() (in Python 2)
#   so perhaps we could do something similar, or just monkeypatch a
#   mock listdir(), so we could unit test this.
def test_MTP_constructor_subpathglobs():
    cons = MTP.constructor(['a'], '/b/c/d/e')
    assert                  not cons('/bravo/bravo/bravo')
    assert                  not cons('/foo/bravo/alpha') # no subpath match
    assert '/b*/c*/d*/e*'    == cons('/foo/bravo/alpha').subpath_glob

@pytest.mark.parametrize('input, expected', (
    ([],                    ([],                None)),
    (['a'],                 (['a'],             None)),
    (['a', 'b', 'c'],       (['a', 'b', 'c'],   None)),
    (['a', 'b', '/c'],      (['a', 'b'],        '/c')),
    (['a', '/b', 'c'],      (['a'],             '/b/c')),
    (['/a', 'b', 'c'],      ([],                '/a/b/c')),
    (['foo', '/bar/baz', 'quux/quux'],
                            (['foo'],           '/bar/baz/quux/quux')),
    ))
def test_split_arg_globs(input, expected):
    assert expected == split_arg_globs(input)

test_matchandsort_targetpaths = (
    '/abc/def/ghi',
    '/ghi/jkl/mno',
    '/def/ghi/jkl',
    '/foo/bar/baz',
)
@pytest.mark.parametrize('globs, expected', (
    # glob          expected first path component
    (['z'],         []),
    ([],            ['abc', 'def', 'foo', 'ghi']),
    (['a'],         ['abc']),
    (['b'],         ['foo']),
    (['[am]'],      ['ghi', 'abc']),
    (['?h',],       ['abc', 'def', 'ghi']),
))
def test_matchandsort(globs, expected):
    ' Functional test of everything outside of actual I/O. '
    matches = matchandsort(globs, test_matchandsort_targetpaths)
    assert str(globs) and \
        expected == map(lambda mp: mp.targetpath[1:4], matches)
