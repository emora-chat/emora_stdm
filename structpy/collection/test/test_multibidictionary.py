import pytest
from structpy.collection.multibidict import Multibidict


def test_constructor():
    mbd = Multibidict({1: ['a'], 2: ['b'], 3: ['c', 'd'], 4: ['a']})
    assert 'a' in mbd[1]
    assert 'b' in mbd[2]
    assert 'a' in mbd[4]
    assert 'd' in mbd[3]
    assert 'c' in mbd[3]
    rev = mbd.reverse()
    assert 1 in rev['a']
    assert 4 in rev['a']
    assert 2 in rev['b']

def test_delete():
    mbd = Multibidict({1: 'a', 2: 'b', 3: 'c', 4: 'a'})
    del mbd[1]
    assert 1 not in mbd
    assert 4 in mbd
    assert 'a' in mbd.reverse()
    assert 4 in mbd.reverse()['a']
