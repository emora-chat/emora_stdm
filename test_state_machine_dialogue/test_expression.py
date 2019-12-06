
import pytest
from expression import Expression as E


def test_literal():
    e = E("hello")
    assert e.match(' hello ')
    assert not e.match('hellx')


def test_conjunction():
    #e = E({'hello', 'there', 'you', 'hey'})
    e = E('<hello, there, you, hey>')
    assert e.match('oh hey hello there whats new with you then')
    assert e.match('oh hey hello there you!')
    assert not e.match('oh hey hello whats new with you then')


def test_disjunction():
    #e = E('hello', 'hey', 'hi', 'how are you')
    e = E('{hello, hey, hi, how are you}')
    assert e.match('hey hello')
    assert e.match('oh hey there')
    assert e.match('hi how are you')
    assert not e.match('how are ya')


def test_inflexible_sequence():
    #e = E(['hello', 'how', 'are', 'you'])
    e = E('[hello, how, are, you]')
    print(e)
    assert e.match('hello, how are you?')
    assert not e.match('hey how are you?')
    assert not e.match('hey hello, so how are you?')


def test_flexible_sequence():
    #e = E(('hello', 'how', 'are', 'you'))
    e = E('(hello, how, are, you)')
    print(e)
    assert e.match('hey hello there how are you today?')
    assert not e.match('hello there you how are your sheep')
    assert not e.match('hello there')


def test_negation():
    e = E('-hello')
    print(e)
    assert e.match('hi how are you')
    assert not e.match('well hello there')
    e = E('-{hello, you}')
    print(e)
    assert e.match('oh hi there')
    assert not e.match('oh hello there')
    assert not e.match('well hello you')
    assert not e.match('oh hello there you')


def test_compound():
    #e = E(('hey', E('hey', 'hello'), {'you', 'are'}, ['good', 'today', {False, 'right'}]))
    e = E('hey {hey, hello} <you, are> [-right, good, today]')
    print(e)
    matches = [
        'hey hello, you are so good today',
        'oh hey hey, are you good today then?'
    ]
    for match in matches:
        assert e.match(match)
    nomatch = [
        'oh hey, are you good today?',
        'hey are you good today?',
        'hey hello, you seem good today',
        'hello hey, are you good today?',
        'hey hey are you good then today?',
        'hey hey you are good today right?'
    ]
    for nm in nomatch:
        assert not e.match(nm)
