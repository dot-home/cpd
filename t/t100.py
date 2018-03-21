from cpd import *

def test_flatten():
    assert ['a', 1, 'b', 2] == flatten([['a', 1], ['b', 2]])

def test_expand_pdglob():
    #   This relies on CWD being set to the dir above `t/`
    #   and $HOME being set to `t/home` in this project.
    assert 't/home/p1/abc' in expand_pdglob('t/home/*/*')
    assert expand_pdglob('~/p?')[1][-9:] == 't/home/p2'

def test_pdmatches():
    p1  = '/projects/one'
    p3  = '/projects/three'
    hp1 = '/home/foo/projects/one'
    hp2 = '/home/foo/projects/two'
    pps = [ p1, p3, hp1, hp2 ]

    def pdm(globs, pps): return list(pdmatches(globs)(pps))

    assert pdm(['no-match'], pps) == []
    assert pdm(['on']      , pps) == [ p1, hp1 ]
    assert pdm(['ho']      , pps) == [ hp1, hp2 ]
    assert pdm(['on', 'ho'], pps) == [ hp1 ]
    assert pdm(['on', 'tw'], pps) == [ ]

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
