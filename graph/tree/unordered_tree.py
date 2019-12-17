
from structpy.graph.tree.tree import Tree

class UnorderedTree(Tree):

    def __init__(self, root):
        self._root = root
        self._parents = {root: set()}
        self._children = {root: None}

    def root(self):
        return self._root

    def children(self, node):
        return self._parents[node]

    def parent(self, node):
        return self._children[node]

    def add_child(self, node, child):
        self._parents[node].add(child)
        if child not in self._parents:
            self._parents[child] = set()
            self._children[child] = node

    def remove_child(self, node, child):
        self._parents[node].remove(child)
        if self._parents[child]:
            pass
        self._children[child] = None

