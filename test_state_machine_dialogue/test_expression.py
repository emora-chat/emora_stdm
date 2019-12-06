
import pytest
from expression import Expression as E


def test_literal():
    e = E("hello")
    assert e.match(' hello ')[0]
    assert not e.match('hellx')[0]


def test_conjunction():
    #e = E({'hello', 'there', 'you', 'hey'})
    e = E('<hello, there, you, hey>')
    assert e.match('oh hey hello there whats new with you then')[0]
    assert e.match('oh hey hello there you!')[0]
    assert not e.match('oh hey hello whats new with you then')[0]


def test_disjunction():
    #e = E('hello', 'hey', 'hi', 'how are you')
    e = E('{hello, hey, hi, how are you}')
    assert e.match('hey hello')[0]
    assert e.match('oh hey there')[0]
    assert e.match('hi how are you')[0]
    assert not e.match('how are ya')[0]


def test_inflexible_sequence():
    #e = E(['hello', 'how', 'are', 'you'])
    e = E('[hello, how, are, you]')
    print(e)
    assert e.match('hello, how are you?')[0]
    assert not e.match('hey how are you?')[0]
    assert not e.match('hey hello, so how are you?')[0]


def test_flexible_sequence():
    #e = E(('hello', 'how', 'are', 'you'))
    e = E('(hello, how, are, you)')
    print(e)
    assert e.match('hey hello there how are you today?')[0]
    assert not e.match('hello there you how are your sheep')[0]
    assert not e.match('hello there')[0]


def test_negation():
    e = E('-hello')
    print(e)
    assert e.match('hi how are you')[0]
    assert not e.match('well hello there')[0]
    e = E('-{hello, you}')
    print(e)
    assert e.match('oh hi there')[0]
    assert not e.match('oh hello there')[0]
    assert not e.match('well hello you')[0]
    assert not e.match('oh hello there you')[0]


def test_assign():
    e = E('hello there %first={jon, sarah} morning')
    print(e)
    assert e.match('hello there jon morning')[0].group('first') == 'jon'
    assert e.match('hello there sarah morning')[0].group('first') == 'sarah'


def test_compound():
    #e = E(('hey', E('hey', 'hello'), {'you', 'are'}, ['good', 'today', {False, 'right'}]))
    e = E('hey {hey, hello} <you, are> [-right, good, today]')
    print(e)
    matches = [
        'hey hello, you are so good today',
        'oh hey hey, are you good today then?'
    ]
    for match in matches:
        assert e.match(match)[0]
    nomatch = [
        'oh hey, are you good today?',
        'hey are you good today?',
        'hey hello, you seem good today',
        'hello hey, are you good today?',
        'hey hey are you good then today?',
        'hey hey you are good today right?'
    ]
    for nm in nomatch:
        assert not e.match(nm)[0]
