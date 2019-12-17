import pytest

from structpy import Pointer, PointerItem

class Simple:

    def __init__(self, a=1, b=2):
        self.one = a
        self.two = b

    def __hash__(self):
        if isinstance(self, Pointer):
            return hash(self.ptr_value)
        else:
            return id(self)

    def __eq__(self, other):
        if isinstance(self, Pointer):
            return self.ptr_value.__eq__(other)
        else:
            return id(self) == id(other)

def test_pointer():
    s = Simple()
    p = PointerItem(s)
    s2 = Simple(5, 6)
    p.set_ptr(s2)
    assert p.one == 5
    assert p.two == 6
    assert +p is s2
    assert isinstance(p, Pointer)
    assert isinstance(p, Simple)

def test_ptr_item():
    s = Simple()
    p = PointerItem(s)
    assert hash(s) == hash(p)

def test_pointer_for_primitive():
    p = Pointer(5)
    assert +p == 5
    p < +p + 2
    assert +p == 7
