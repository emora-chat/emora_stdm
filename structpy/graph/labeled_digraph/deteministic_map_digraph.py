
from structpy.graph.labeled_digraph.labeled_digraph import LabeledDigraph


class DeterministicMapDigraph(LabeledDigraph):

    def __init__(self, arcs=None):
        """
        *_sources_labels_targets* : `dict<source: dict<label: target>>`

        *_targets_labels_sources* : `dict<target: dict<label: source>>`

        *_sources_targets_label* : `dict<source: dict<target: label>>`
        """
        self._sources_labels_targets = {}
        self._targets_labels_sources = {}
        self._sources_target_label = {}
        if arcs is not None:
            for arc in arcs:
                self.add(*arc)

    def nodes(self):
        return self._sources_labels_targets.keys()

    def add_node(self, node):
        self._sources_labels_targets[node] = {}
        self._targets_labels_sources[node] = {}
        self._sources_target_label[node] = {}

    def add_arc(self, source, target, label):
        self._sources_labels_targets[source][label] = target
        self._targets_labels_sources[target][label] = source
        self._sources_target_label[source][target] = label

    def remove_node(self, node):
        sources = self.sources(node)
        targets = self.targets(node)
        for source in sources:
            self.remove_arc(source, node)
        for target in targets:
            self.remove_arc(node, target)
        del self._sources_target_label[node]
        del self._targets_labels_sources[node]
        del self._sources_labels_targets[node]

    def remove_arc(self, source, target):
        if self.has_arc(source, target):
            label = self.label(source, target)
            del self._sources_labels_targets[source][label]
            del self._targets_labels_sources[target][label]
            del self._sources_target_label[source][target]

    def targets(self, source):
        return set(self._sources_labels_targets[source].values())

    def sources(self, target):
        return set(self._targets_labels_sources[target].values())

    def target(self, source, label):
        return self._sources_labels_targets[source][label]

    def source(self, target, label):
        return self._targets_labels_sources[target][label]

    def label(self, source, target):
        return self._sources_target_label[source][target]

    def arcs(self, node=None):
        if node is None:
            for source in self._sources_target_label:
                for target, label in self._sources_target_label[source].items():
                    yield source, target, label
        return self.arcs_out(node).update(self.arcs_in(node))

    def has_arc(self, source, target, label=None):
        return source in self._sources_target_label \
                and target in self._sources_target_label[source] \
                and self._sources_target_label[source][target] == label

    def has_arc_label(self, source, label):
        return label in self._sources_labels_targets[source]

