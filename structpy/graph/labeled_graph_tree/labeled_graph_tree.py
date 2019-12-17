
from structpy.language.simple import single
from structpy.graph.labeled_digraph.map_digraph import MapDigraph as Net

class LabeledGraphTree:

    def __init__(self, root=None, graph=None):
        self._root = root
        if graph is None:
            graph = Net()
            graph.add_node(root)
        self._graph = graph

    def graph(self):
        """

        """
        return self._graph

    def root(self):
        """

        """
        return self._root

    def set_root(self, root):
        """

        """
        self._root = root

    def children(self, node, label=None):
        """

        """
        return self.graph().targets(node, label)

    def parent(self, node):
        """

        """
        if node == self.root():
            return None
        else:
            return single(self.graph().sources(node))

    def label(self, parent, child):
        """

        """
        return self.graph().label(parent, child)

    def add(self, parent, child, label):
        """

        """
        return self.graph().add(parent, child, label)

    def remove(self, child):
        """

        """
        return self.graph().remove(child)
