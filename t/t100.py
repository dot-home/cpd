from cpd import *

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
