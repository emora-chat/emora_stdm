
from structpy.graph.labeled_graph.labeled_graph_base import LabeledGraphBase


class MapGraph(LabeledGraphBase):

    def __init__(self, arcs=None):
        LabeledGraphBase.__init__(self)
        self._arcs = {}
        for arc in arcs:
            self.add(*arc)

    def add_node(self, node):
        self._arcs[node] = {}

    def add_arc(self, source, target, label):
        self._arcs[source][label] = target

    def add(self, source, target, label):
        if not self.has_node(source):
            self.add_node(source)
        if not self.has_node(target):
            self.add_node(target)
        self.add_arc(source, target, label)

    def remove_node(self, node):
        del self._arcs[node]
        for source in self._arcs:
            for label in self._arcs.keys():
                if self._arcs[source][label] == node:
                    del self._arcs[source][label]

    def remove_arc(self, source, target):
        for label in self._arcs[source].keys():
            if self._arcs[source][label] == target:
                del self._arcs[source][label]
                return

    def remove_arc_by_label(self, source, label):
        del self._arcs[source][label]

    def has_node(self, node):
        return node in self._arcs

    def has_arc(self, source, target, label=None):
        return source in self._arcs \
               and ((label is None and target in self._arcs.values())
                    or self._arcs[source][target] == label)

    def nodes(self):
        return self._arcs.keys()

    def arcs(self):
        for source in self._arcs:
            yield from [(source, target, label) \
                        for label, target in self._arcs[source].items()]

    def len_nodes(self):
        return len(self._arcs)

    def len_arcs(self):
        return sum(len(self._arcs[source]) for source in self._arcs)

    def targets(self, source):
        return self._arcs[source].values()

    def target(self, source, label):
        return self._arcs[source][label]

    def sources(self, target):
        for s, t, l in self.arcs():
            if target == t:
                yield s

    def source(self, target, label):
        for s, t, l in self.arcs():
            if target == t and label == l:
                return s

    def arcs_out(self, source):
        return [(source, target, label) for label, target in self._arcs[source].items()]

    def arcs_in(self, target):
        for s, t, l in self.arcs():
            if t == target:
                yield s, t, l

