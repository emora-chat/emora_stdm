
import pytest

from structpy.graph.net import Network, NetworkNode

n = [NetworkNode(x) for x in range(6)]

@pytest.fixture
def net():
    net = Network()
    for node in n:
        net.add_node(node)
    net.add_arc(n[1], n[2], 'a')
    n[1].add(n[3], 'a')
    net.add_arc(n[2], n[3], 'b')
    net.add_arc(n[2], n[1], 'c')
    n[3].add(n[4], 'd')
    net.add_arc(n[4], n[5], 'e')
    return net

def test_get_label(net):
    assert n[1].label(n[2]) == 'a'
    assert net.label(n[1], n[2]) == 'a'
    assert net.label(n[1], n[3]) == 'a'
    assert net.label(n[2], n[3]) == 'b'
    assert n[2].label(n[1]) == 'c'


def test_get_targets(net):
    assert set(net.targets(n[1])) == {n[2], n[3]}
    assert set(net.targets(n[2])) == {n[3], n[1]}
    assert set(net.targets(n[3])) == {n[4]}

def test_get_sources(net):
    assert set(net.sources(n[1])) == {n[2]}
    assert set(net.sources(n[2])) == {n[1]}
    assert set(net.sources(n[3])) == {n[1], n[2]}

def test_nodes(net):
    nodes = set(net.nodes())
    assert nodes == {n[0], n[1], n[2], n[3], n[4], n[5]}

def test_arcs(net):
    arcs = set(net.arcs())
    assert arcs == {
        (n[1], n[2], 'a'),
        (n[1], n[3], 'a'),
        (n[2], n[3], 'b'),
        (n[2], n[1], 'c'),
        (n[3], n[4], 'd'),
        (n[4], n[5], 'e')
    }

def test_len_nodes(net):
    assert net.len_nodes() == 6

def test_len_arcs(net):
    assert net.len_arcs() == 6

def test_node(net):
    node = net.node(1)
    assert set(node.targets()) == {n[2], n[3]}
