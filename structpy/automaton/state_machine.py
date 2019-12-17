
from enum import Enum
from structpy.graph import Database
from structpy.graph.labeled_digraph import DeterministicMapDigraph
from structpy.language.simple import single

Graph = Database(DeterministicMapDigraph)


class Functions(Enum):
    Score = 0
    Transition = 1


class StateMachine:

    def __init__(self, arcs=None, initial_state=None):
        self._graph = Graph(arcs)
        self._initial_state = initial_state
        if initial_state is not None:
            self.set_initial_state(initial_state)
        self._state = self._initial_state

    def set_initial_state(self, initial_state):
        self._initial_state = initial_state
        if not self._graph.has_node(initial_state):
            self.add_state(initial_state)

    def add_state(self, state):
        if not self._graph.has_node(state):
            self._graph.add_node(state)
        else:
            raise KeyError("state {} already exists".format(str(state)))

    def has_state(self, state):
        return self._graph.has_node(state)

    def add_transition(self, source_state, target_state, transition, transition_fn=None):
        if not self._graph.has_arc(source_state, target_state):
            self._graph.add(source_state, target_state, transition)
            if transition_fn is not None:
                self._graph.arc_data(source_state, target_state)[Functions.Transition] = transition_fn
        else:
            raise KeyError("transition {}, {} already exists with label {}".format(
                str(source_state), str(target_state), str(transition)))

    def has_transition(self, source_state, target_state, transition=None):
        return self._graph.has_arc(source_state, target_state, transition)

    def graph(self):
        return self._graph

    def state(self):
        return self._state

    def reset(self):
        self._state = self._initial_state

    def next(self, input=None):
        source = self._state
        if not self._graph.has_arc_label(self._state, input):
            scores = []
            for s, t, l in self._graph.arcs_out(self._state):
                score_fn = self._graph.arc_data(s, t)[Functions.Score]
                score = score_fn(
                    input,
                    self._graph.node(s),
                    self._graph.node(t),
                    self._graph.arc(s, t, l)
                )
                scores.append((score, s, t, l))
            _, __, target, label = max(scores)
            self._state = target
        else:
            self._state = self._graph.target(self._state, input)
            target = self._state
            label = self._graph.label(source, target)
        if Functions.Transition in self._graph.arc_data(source, target):
            transition_fn = self._graph.arc_data(source, target)[Functions.Transition]
            transition_fn(
                input,
                self._graph.node(source),
                self._graph.node(target),
                self._graph.arc(source, target, label)
            )
        return self._state

    def jump(self, state):
        self._state = state

    def remove_transition(self, source, target):
        self._graph.remove_arc(source, target)

    def remove_state(self, state):
        self._graph.remove_node(state)

    def __str__(self):
        return 'StateMachine<{}>'.format(str(self._state))
