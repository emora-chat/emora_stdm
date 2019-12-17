from structpy import interface
from structpy import I
import pytest

class Cls:

    def __init__(self, x):
        self._x = x

    def x(self):
        return self._x

    def get_value(self):
        return self.x()

    def __str__(self):
        return 'TestClass(' + str(self._x) + ')'

def test_constructor():
    tc = Cls(5)
    i = I(tc)
    assert i.x() == 5

def test_add_function():
    tc = Cls(5)
    i = I(tc)
    i.foo = lambda n: n ** 2
    assert i.foo(3) == 9

def test_add_method():
    tc = Cls(5)
    i = I(tc,
          foo = (lambda self, n: self._x + n),
          bar = (lambda self: -1)
          )
    assert i.foo(2) == 7
    t2 = Cls(1)
    i2 = I(t2, foo=(lambda self: self._x + 100))
    assert i2.foo() == 101
    assert i.foo(2) == 7
    assert i.bar() == -1
    with pytest.raises(AttributeError):
        i2.bar()

def test_switch_method():
    tc = Cls(5)
    i = I(tc,
          baz=tc.x,
          x=(lambda self, y: self._x + y),
          foo=(lambda self, n: self._x + n),
          bar=(lambda self: -1)
          )
    assert i.baz() == 5
    assert i.x(2) == 7
    assert i.foo(3) == 8
    assert i.bar() == -1

    t2 = Cls(1)
    i2 = I(t2, foo=(lambda self: self._x + 100))
    assert i2.foo() == 101
    assert i2.x() == 1
    assert i.foo(2) == 7
    assert i.bar() == -1
    with pytest.raises(AttributeError):
        i2.bar()

def test_interface_function():
    tc = Cls(5)
    i_func = interface(
        bar=(lambda self, y: self._x + y)
    )
    i = i_func(tc)
    assert i.bar(3) == 8
    assert i.x() == 5

'''
does not work yet (see CreateInterface)
def test_interface_inheritance():
    tc = Cls(5)
    i = I(
        tc,
        x=lambda self: 10,
        y=lambda self: 6
    )
    assert i.x() == 10
    assert i.get_value() == 10
    with pytest.raises(AttributeError):
        tc.y()
    assert tc.get_value() == 5
'''
