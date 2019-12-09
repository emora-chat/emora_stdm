
import pytest
from expression import Expression as E
from expression import VirtualExpression as VE


def test_literal():
    e = E("hello")
    assert e.match(' hello ')[0]
    assert not e.match('hellx')[0]


def test_conjunction():
    e = E('<hello, there, you, hey>')
    assert e.match('oh hey hello there whats new with you then')[0]
    assert e.match('oh hey hello there you!')[0]
    assert not e.match('oh hey hello whats new with you then')[0]


def test_disjunction():
    e = E('{hello, hey, hi, how are you}')
    assert e.match('hey hello')[0]
    assert e.match('oh hey there')[0]
    assert e.match('hi how are you')[0]
    assert not e.match('how are ya')[0]


def test_inflexible_sequence():
    e = E('[hello, how, are, you]')
    print(e)
    assert e.match('hello, how are you?')[0]
    assert not e.match('hey how are you?')[0]
    assert not e.match('hey hello, so how are you?')[0]


def test_flexible_sequence():
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


def test_regex():
    e = E('hello /(?<var>[a-z A-Z_0-9]+)/ there')
    print(e)
    match, vars = e.match('hello you there')
    assert match
    assert vars['var'].strip() == 'you'
    match, vars = e.match('hello abcd')
    assert not match


def test_assign():
    e = E('hello there %first={jon, sarah} morning')
    print(e)
    assert e.match('hello there jon morning')[1]['first'] == 'jon'
    assert e.match('hello there then sarah morning')[1]['first'] == 'sarah'


def test_var():
    e = E('{i, you}, {can, will, may, might}, {bake, make, cook}, $food, {tonight, tomorrow}')
    print(e)
    assert e.match('i might cook pasta tomorrow', {'food': 'pasta'})[0]
    assert not e.match('i might cook steak tomorrow', {'food': 'pasta'})[0]
    assert not e.match('i might cook pasta tomorrow', {'food': 'steak'})[0]
    assert not e.match('i might cook pasta tomorrow')[0]


def test_virtual_expression():
    e = VE('i, saw, {a, the} %a=animal, yesterday',
           {
                'animal': (lambda item: item.strip() in {'dog', 'bird', 'cat'})
           })
    print(e)
    match, vars = e.match('i saw the dog yesterday')
    assert match
    assert vars['a'] == 'dog'
    match, vars = e.match('i saw the horse yesterday')
    assert not match


def test_compound():
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
