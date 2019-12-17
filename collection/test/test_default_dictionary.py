
import pytest

from structpy.collection import DefaultDictionary

def test_constructor():
    d = DefaultDictionary()
    d.update({1: 2, 3: 4, 5: 6})
    assert d == {1: 2, 3: 4, 5: 6}

def test_default():
    d = DefaultDictionary(lambda x: x * 3)
    assert d[1] == 3
    assert d[2] == 6
    assert d[45] == 135
    assert len(d) == 0

