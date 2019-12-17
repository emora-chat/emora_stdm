
from structpy.graph.net.network_node import NetworkNode
from structpy.collection import Bidictionary
from structpy.graph.labeled_digraph import LabeledDigraph

class Net(LabeledDigraph):

    Node = NetworkNode

    def __init__(self):

        # node object : node value
        self._nodes = Bidictionary()

    def nodes(self):
        return self._nodes.backward().keys()

    def node(self, value):
        return self._nodes.backward()[value]

    def add(self, node, target=None, label=None):
        if node not in self._nodes.backward():
            node = NetworkNode(node)
        else:
            node = self.node(node)
        if target is None:
            return self.add_node(node)
        else:
            if target not in self._nodes.backward():
                target = NetworkNode(target)
            else:
                target = self.node(target)
            self.add_arc(node, target, label)

    def add_node(self, node):
        self._nodes[node] = node.value()
        return node

    def add_arc(self, source, target, label):
        source = self.node(source)
        target = self.node(target)
        source.add(target, label)

    def remove_node(self, node):
        node.delete()
        del self._nodes[node]

    def remove_arc(self, source, target):
        source = self.node(source)
        target = self.node(target)
        source.remove(target)

    def targets(self, source, label=None):
        source = self.node(source)
        return {self._nodes[x] for x in source.targets(label)}

    def label(self, source, target):
        source = self.node(source)
        target = self.node(target)
        return source.label(target)

    def sources(self, target, label=None):
        target = self.node(target)
        return {self._nodes[x] for x in target.sources(label)}

    def arcs(self):
        arcs = set()
        for node in self.nodes():
            for target in self.targets(node):
                label = self.label(node, target)
                arcs.add((node, target, label))
        return arcs
