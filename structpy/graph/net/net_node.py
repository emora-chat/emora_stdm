
class NetNode:

    def __init__(self, value=None, net=None):
        self._node_value = value

        # node value : label
        self._targets_label = {}

        # label : set of node values
        self._labels_targets = {}

        # label : set of node values
        self._labels_sources = {}

        # the graph this node is a part of
        self._net = net

    def value(self):
        return self._node_value

    def set_value(self, value):
        self._node_value = value

    def net(self):
        return self._net

    def set_net(self, net):
        self._net = net

    def targets(self, label=None):
        if label is None:
            return self._targets_label.keys()
        else:
            return self._labels_targets[label]

    def sources(self, label=None):
        if label is None:
            sources = set()
            for sset in self._labels_targets.values():
                sources.update(sset)
            return sources
        else:
            return self._labels_sources[label]

    def add(self, target, label=None):
        self._net.add_node(target)
        self._targets_label[target] = label
        if label not in self._labels_targets:
            self._labels_targets[label] = set()
        self._labels_targets[label].add(target)
        if label not in target._labels_sources:
            target._labels_sources[label] = set()
        target._labels_sources[label].add(self)

    def remove(self, target):
        label = self._targets_label[target]
        target._labels_sources[label].remove(self)
        if not target._labels_sources[label]:
            del target._labels_sources[label]
        del self._targets_label[target]
        self._labels_targets[label].remove(target)
        if not self._labels_targets[label]:
            del self._labels_targets[label]
        self._net.remove_node(target)

    def delete(self):
        for source in self.sources():
            source.remove(self)
        for target in self.targets():
            self.remove(target)
