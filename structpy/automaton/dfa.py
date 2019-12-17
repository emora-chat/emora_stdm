
from structpy.graph.map_graph.map_graph import MapGraph as Graph


class DFA:

    def __init__(self, arcs=None, initial_state=None):
        self._graph = Graph()
        self._initial_state = None
        self._state = self._initial_state

    def graph(self):
        return self._graph

    def state(self):
        return self._state

    def reset(self):
        self._state = self._initial_state

    def next(self, input=None):
        self._state = self._graph.target(self._state, input)
