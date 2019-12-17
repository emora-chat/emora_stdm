
from structpy.graph.labeled_digraph.labeled_digraph import LabeledDigraph


class SourceMapDigraph(LabeledDigraph):
    """
    Similar to MapDigraph but with unique labels on out arcs
    """

    def __init__(self, arcs=None):
        """
        *_sources_labels_targets* : `dict<source: dict<label: set<target>>>`

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
        if label not in self._sources_labels_targets[source]:
            self._sources_labels_targets[source][label] = set()
        self._sources_labels_targets[source][label].add(target)
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
        label = self.label(source, target)
        self._sources_labels_targets[source][label].remove(target)
        if not self._sources_labels_targets[source][label]:
            del self._sources_labels_targets[source][label]
        del self._targets_labels_sources[target][label]
        del self._sources_target_label[source][target]

    def targets(self, source, label=None):
        if label is None:
            targets = set()
            for label in self._sources_labels_targets[source]:
                targets.update(self._sources_labels_targets[source][label])
            return targets
        else:
            return set(self._sources_labels_targets[source][label])

    def sources(self, target):
        return set(self._targets_labels_sources[target].values())

    def source(self, target, label):
        return self._targets_labels_sources[target][label]

    def label(self, source, target):
        return self._sources_target_label[source][target]

    def arcs(self, node=None):
        if node is None:
            arcs = set()
            for source in self._sources_target_label:
                for target in self._sources_target_label[source]:
                    label = self._sources_target_label[source][target]
                    arcs.add((source, target, label))
            return arcs
        else:
            return self.arcs_out(node).update(self.arcs_in(node))

    def has_arc(self, source, target, label=None):
        if label is None:
            return target in self._sources_target_label[source]
        else:
            tl = self._sources_target_label[source]
            return target in tl and tl[target] == label
