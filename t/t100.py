import pytest

from cpd import *


def test_flatten():
    assert ['a', 1, 'b', 2] == flatten([['a', 1], ['b', 2]])

def test_reverse():
    assert    [3,2,1] == reverse([1,2,3])

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

@pytest.mark.parametrize('globs, path, rkey', [
    #   Sort key is '0' for match, '1' for not, reversed
    (['a'       ],  '/charlie/bravo/alpha',     '011'),
    (['a'       ],  '/alpha/bravo/alpha',       '010'),
    (['b'       ],  '/bravo/bravo/bravo',       '000'),
    (['a', 'b'  ],  '/bravo/alpha/charlie',     '100'),
    (['a'       ],  '/foo/bravo/alpha',         '011'),
    (['b'       ],  '/bravo/bravo/bravo',       '000'),
    (['a', 'b'  ],  '/bravo/alpha/charlie',     '100'),

    pytest.param(['a', 'al' ], '/bravo/alpha/charlie', '101',
        marks=pytest.mark.xfail(strict=True, reason='bug: both globs match'
            ' but we return just the first glob that matched, internally')),

    #   Glob testing
    (['',       ],  '/alpha/bravo/charlie',     '111'), # XXX no matches?
    (['?r',     ],  '/alpha/bravo/charlie',     '101'),
    (['??a',    ],  '/alpha/bravo/charlie',     '001'),
    (['a*p',    ],  '/alpha/bravo/charlie',     '110'),
    (['[ab]',   ],  '/alpha/bravo/charlie',     '100'),
    (['[ac]',   ],  '/alpha/bravo/charlie',     '010'),
    (['*[xyz]'  ],  '/nope/yes/aaaz/abxcd',     '0001'),
])
def test_makesortkey(globs, path, rkey):
    assert (rkey, path) == (MatchingPath.makesortkey(globs)(path), path)

def test_makesortkey_notallmatch():
    inputs = [
        (['x', 'b'],    '/bravo/alpha/charlie'),
        (['a'],         '/bravo/bravo/bravo'),
        (['a*b'],       '/alpha/bravo'),
    ]
    for globs, path in inputs:
        with pytest.raises(MatchingPath.AllGlobsMustMatch):
            MatchingPath.makesortkey(globs)(path)

def mp(path):
    ''' Our standard test MatchingPath with a fixed glob.
        Matching:     bravo, delta
        Non-matching: alpha, charlie, echo
    '''
    return MatchingPath(path, ['b', 'd'])

def test_MatchingPath_construction():
    ''' A MatchingPath must always have at least one component matching
        each glob. This is an integration test; the full test of the
        check is test_MatchingPath_makesortkey_notallmatch.
    '''
    assert mp('/charlie/bravo/delta')
    with pytest.raises(MatchingPath.AllGlobsMustMatch):
        assert mp('/charlie/bravo/echo')

def test_MatchingPath_ordering():
    #   XXX This test assumes that all component_globs match a component!

    with pytest.raises(MatchingPath.Incomparable):
        mp('/bravo/delta') == MatchingPath('/bravo/delta', ['b', 'de'])
    with pytest.raises(MatchingPath.Incomparable):
        mp('/bravo/delta') < MatchingPath('/bravo/delta', ['b', 'de'])

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

def test_MatchingPath_constructor():
    m = MatchingPath.constructor
    assert     m(['a'       ])('/foo/bravo/alpha')
    assert not m(['a'       ])('/bravo/bravo/bravo')
    assert     m(['b'       ])('/bravo/bravo/bravo')
    assert     m(['a', 'b'  ])('/bravo/alpha/charlie')
    assert not m(['x', 'b'  ])('/bravo/alpha/charlie')
