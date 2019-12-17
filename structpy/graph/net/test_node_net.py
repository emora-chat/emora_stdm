
import pytest

from structpy.graph.net import Net

from structpy.graph.element import Node


types = [Net]

@pytest.mark.parametrize('cls', types)
def test_constructor(cls):
    net = cls()

@pytest.fixture(params=types)
def net(request):
    cls = request.param
    n = cls()
    n.add(1)
    n.add(2)
    n.add(3)
    n.add(4)
    n.add(5)
    n.add_arc(1, 2, 'a')
    n.add_arc(1, 3, 'a')
    n.add_arc(2, 3, 'b')
    n.add_arc(2, 1, 'c')
    n.add_arc(3, 4, 'd')
    n.add_arc(4, 5, 'e')
    return n

def test_get_label(net):
    assert net.label(1, 2) == 'a'
    assert net.label(1, 3) == 'a'
    assert net.label(2, 3) == 'b'
    assert net.label(2, 1) == 'c'

def test_get_targets(net):
    assert set(net.targets(1)) == {2, 3}
    assert set(net.targets(2)) == {3, 1}
    assert set(net.targets(3)) == {4}

def test_get_sources(net):
    assert set(net.sources(1)) == {2}
    assert set(net.sources(2)) == {1}
    assert set(net.sources(3)) == {1, 2}

def test_nodes(net):
    nodes = set(net.nodes())
    assert nodes == {1, 2, 3, 4, 5}

def test_arcs(net):
    arcs = set(net.arcs())
    assert arcs == {
        (1, 2, 'a'),
        (1, 3, 'a'),
        (2, 3, 'b'),
        (2, 1, 'c'),
        (3, 4, 'd'),
        (4, 5, 'e')
    }

def test_len_nodes(net):
    assert net.len_nodes() == 5

def test_len_arcs(net):
    assert net.len_arcs() == 6

def test_node(net):
    n = net.node(1)
    assert set(n.targets()) == {net.node(2), net.node(3)}