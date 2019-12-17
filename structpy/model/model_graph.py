
from structpy.collection import DefaultDictionary
from structpy.graph import Database
from structpy.graph.labeled_digraph import SourceMapDigraph
Graph = Database(SourceMapDigraph)
from enum import Enum


class _Model(Enum):
    PULL = 0
    PUSH = 1
    COUNT = 2


class ModelGraph(Graph):

    def __init__(self, arcs=None):
        Graph.__init__(self, arcs)
        self._update = DefaultDictionary(lambda ptr: [+ptr])  # dict<node: list<float>>
        self._pooling = lambda ls: sum(ls) / len(ls)

    def add_arc(self, source, target, label=None):
        if label is None:
            if _Model.COUNT not in self.data(target):
                label = 0
                self.data(target)[_Model.COUNT] = 1
            else:
                label = self.data(target)[_Model.COUNT]
                self.data(target)[_Model.COUNT] += 1
        Graph.add_arc(self, source, target, label)

    def set_pooling(self, pooling_function):
        self._pooling = pooling_function

    def add_pull(self, node, function_ptr):
        self.data(node)[_Model.PULL] = function_ptr

    def add_push(self, node, function_ptr):
        self.data(node)[_Model.PUSH] = function_ptr

    def update(self):
        for ptr, vals in self._update.items():
            ptr.set_ptr(self._pooling(vals))
        self._update.clear()

    def set_update(self, node, value):
        if node not in self._update:
            self._update[node] = []
        self._update[node].append(value)

    def get_update(self, node):
        return self._update[node]

    def pull_update(self, node):
        source_map = {self.label(source, node): +source
                      for source in self.sources(node)}
        self.set_update(node, self.data(node)[_Model.PULL](+node, source_map))

    def push_update(self, node):
        source_map = {self.label(source, node): +source
                      for source in self.sources(node)}
        target_map = {self.label(node, target): +target
                      for target in self.targets(node)}
        self.data(node)[_Model.PUSH](+node, source_map, target_map)
        for label, value in target_map.items():
            for target in self.targets(node, label):
                self.set_update(target, value)


