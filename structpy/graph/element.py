
from functools import partial


class Node:

    def __init__(self, graph, value):
        self.value = value
        self._graph = graph

    def __getattr__(self, function):
        fptr = self._graph.__getattribute__(function)
        return partial(fptr, self.value)


class Arc:

    def __init__(self, graph, source, target, label=None):
        if label is None:
            self.value = (source, target)
            self._graph = graph
        else:
            self.value = (source, target, label)
            self._graph = graph

    def source(self):
        return self.value[0]

    def target(self):
        return self.value[1]

    def label(self):
        return self.value[2]

    def data(self):
        return self._graph.arc_data(*self.value)

    def __getattr__(self, function):
        fptr = self._graph.__getattribute__(function)
        return partial(fptr, *self.value)
