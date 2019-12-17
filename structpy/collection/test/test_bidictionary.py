
import pytest

from structpy.collection import Bidictionary

@pytest.fixture
def bidict():
    d = Bidictionary({'a': 1, 'b': 2, 'c': 3})
    return d

def test_constructor(bidict):
    assert bidict.forward() == {'a': 1, 'b': 2, 'c': 3}

def test_add(bidict):
    assert bidict['a'] == 1
    bidict['d'] = 4
    assert bidict['d'] == 4
    assert bidict.backward()[4] == 'd'
    assert bidict.backward()[1] == 'a'
    assert len(bidict) == 4

def test_reverse(bidict):
    rev = bidict.reverse()
    assert rev[1] == 'a'
    assert rev.backward()['a'] == 1