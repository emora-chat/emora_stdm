
from structpy.graph.labeled_digraph.labeled_digraph import LabeledDigraph

class LabeledOrderedDigraph(LabeledDigraph):

    def __init__(self, other_labeled_graph=None):
        """
        *_sources_targets_label*: `dict<list<tuple<target, label>>>`
        """
        self._sources_targets_label = {}
        self._targets_sources = {}
        if other_labeled_graph is not None:
            for arc in other_labeled_graph.arcs():
                self.add(*arc)

    def nodes(self):
        return self._sources_targets_label.keys()

    def add_node(self, node):
        self._sources_targets_label[node] = {}
        self._targets_sources[node] = []

    def add_arc(self, source, target, label):
        pass
