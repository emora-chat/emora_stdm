
from structpy.graph.labeled_digraph import LabeledDigraph
from structpy.graph.net.network_node import NetworkNode
from structpy.collection import Bidictionary

class Network(LabeledDigraph):

    Node = NetworkNode

    def __init__(self):

        # node object : node value
        self._nodes = Bidictionary()

    def nodes(self):
        return self._nodes.keys()

    def node(self, value):
        return self._nodes.backward()[value]

    def add(self, node, target=None, label=None):
        if target is None:
            return self.add_node(node)
        else:
            self.add_arc(node, target, label)

    def add_node(self, node):
        self._nodes[node] = node.value()
        return node

    def add_arc(self, source, target, label):
        source.add(target, label)

    def remove_node(self, node):
        node.delete()
        del self._nodes[node]

    def remove_arc(self, source, target):
        source.remove(target)

    def targets(self, source, label=None):
        return source.targets(label)

    def label(self, source, target):
        return source.label(target)

    def sources(self, target, label=None):
        return target.sources(label)


