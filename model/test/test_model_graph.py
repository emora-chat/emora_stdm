import pytest
from structpy.model import ModelGraph
from structpy import Pointer as Ptr
from functools import reduce

def test_model():
    a = Ptr(1.0)
    b = Ptr(2.0)
    c = Ptr(3.0)
    d = Ptr(4.0)
    e = Ptr(5.0)
    f = Ptr(6.0)
    g = ModelGraph([
        (a, b, 'u'),
        (a, c, 'v'),
        (b, d, 'w'),
        (d, e, 'x'),
        (e, b, 'y'),
        (e, f, 'z')
    ])

    def add(node, sources, targets):
        s = sum(sources.values())
        for target in targets:
            targets[target] = s
        return targets

    def mult(node, sources, targets):
        s = reduce(lambda x, y: x * y, sources.values())
        for target in targets:
            if target != 'x':
                targets[target] = s
        return targets

    g.add_push(b, add)

    assert +d == 4.0
    g.push_update(b)
    assert +d == 4.0
    assert g.get_update(d) == [6.0]
    g.update()
    assert +d == 6.0



