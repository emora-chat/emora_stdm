
import pytest
from structpy.graph.labeled_graph_tree import LabeledGraphTree as Tree
from structpy.graph.labeled_digraph import MapDigraph
from structpy.language import I

@pytest.fixture
def t():
    net = MapDigraph(I(
        [
            (0, 1, 'a'),
            (0, 2, 'b'),
            (1, 3, 'c'),
            (1, 4, 'c'),
            (2, 5, 'd'),
            (5, 6, 'e')
        ],
        arcs=(lambda self: self)
    ))
    tree = Tree(0, net)
    return tree

def test_constructor():
    tree = Tree(0)
    assert tree.root() == 0
    assert set(tree.children(0)) == set()

def test_children(t):
    assert set(t.children(0)) == {1, 2}
    assert set(t.children(1)) == {3, 4}
    assert set(t.children(2)) == {5}

def test_labeled_children(t):
    assert set(t.children(1, 'c')) == {3, 4}
    assert set(t.children(0, 'a')) == {1}

def test_label(t):
    assert t.label(0, 1) == 'a'
    assert t.label(0, 2) == 'b'

def test_parent(t):
    assert t.parent(0) == None
    assert t.parent(1) == 0
    assert t.parent(2) == 0
    assert t.parent(4) == 1
    assert t.parent(6) == 5

def test_add():
    tree = Tree(0)
    tree.add(0, 1, 'a')
    tree.add(0, 2, 'b')
    tree.add(2, 3, 'c')
    assert set(tree.graph().arcs()) == {(0, 1, 'a'), (0, 2, 'b'), (2, 3, 'c')}

