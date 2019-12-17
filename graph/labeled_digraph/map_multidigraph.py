
from structpy.graph.labeled_digraph.map_digraph import MapDigraph
from structpy.language.simple import single


class MapMultidigraph(MapDigraph):
    """
    *_sources_labels_targets* : `dict<source: dict<label: set<target>>>`

    *_targets_labels_sources* : `dict<target: dict<label: set<source>>>`

    *_sources_targets_label* : `dict<source: dict<target: set<label>>>`
    """

    def add_arc(self, source, target, label):
        if label not in self._sources_labels_targets[source]:
            self._sources_labels_targets[source][label] = set()
        self._sources_labels_targets[source][label].add(target)
        if label not in self._targets_labels_sources[target]:
            self._targets_labels_sources[target][label] = set()
        self._targets_labels_sources[target][label].add(source)
        if target not in self._sources_target_label[source]:
            self._sources_target_label[source][target] = set()
        self._sources_target_label[source][target].add(label)

    def remove_arc(self, source, target, label):
        self._sources_labels_targets[source][label].remove(target)
        if not self._sources_labels_targets[source][label]:
            del self._sources_labels_targets[source][label]
        self._targets_labels_sources[target][label].remove(source)
        if not self._targets_labels_sources[target][label]:
            del self._targets_labels_sources[target][label]
        self._sources_target_label[source][target].remove(label)
        if not self._sources_target_label[source][target]:
            del self._sources_target_label[source][target]

    def remove_arcs(self, source, target):
        labels = self.label(source, target)
        for label in labels:
            self.remove_arc(source, target, label)

    def label(self, source, target):
        return self._sources_target_label[source][target]

    def labels(self, source, target):
        return self._sources_target_label[source][target]

    def arcs(self, node=None, label=None):
        if node is None:
            arcs = set()
            for source in self._sources_target_label:
                for target in self._sources_target_label[source]:
                    labels = self._sources_target_label[source][target]
                    for label in labels:
                        arcs.add((source, target, label))
            return arcs
        else:
            return self.arcs_out(node, label).update(self.arcs_in(node, label))

    def arcs_out(self, node, label=None):
        if label is None:
            arcs = set()
            for target in self.targets(node):
                labels = self.label(node, target)
                for label in labels:
                    arcs.add((node, target, label))
            return arcs
        else:
            arcs = set()
            for target in self.targets(node, label):
                arcs.add((node, target, label))
            return arcs

    def arcs_in(self, node, label=None):
        if label is None:
            arcs = set()
            for source in self.sources(node):
                labels = self.label(source, node)
                for label in labels:
                    arcs.add((source, node, label))
            return arcs
        else:
            arcs = set()
            for source in self.sources(node, label):
                arcs.add((source, node, label))
            return arcs

    def has_arc(self, source, target, label=None):
        if label is None:
            return source in self._sources_target_label and target in self._sources_target_label[source]
        else:
            if source not in self._sources_target_label:
                return False
            tl = self._sources_target_label[source]
            return target in tl and label in tl[target]
