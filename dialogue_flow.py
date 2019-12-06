
import random
from structpy.automaton import StateMachine
from structpy.graph.labeled_digraph import DeterministicMapDigraph as Graph
from expression import Expression
from enum import Enum


class DialogueTransition:

    def __init__(self, source, target, nlu, nlg, settings='', nlg_vars=None):
        self.source = source
        self.target = target
        self.nlu = nlu
        self.nlg = nlg
        self.nlg_vars = {} if not nlg_vars else nlg_vars
        self.settings = settings
        self.update_settings()

    def update_settings(self):
        if 'e' in self.settings:
            self.nlu_score = 0
            self.nlu_min = -99
            self.nlg_score = 1
            self.nlg_min = -99
        else:
            self.nlu_score = 10
            self.nlu_min = 1
            self.nlg_score = 10
            self.nlg_min = 1

    def user_transition_check(self, utterance):
        if not self.nlu:
            return 0, {}
        else:
            match = self.nlu.match(utterance)
            if match:
                return 10, {}
            else:
                return 0, {}

    def system_transition_check(self):
        if not self.nlg:
            return 0, {}
        else:
            return self.nlg_score, self.nlg_vars

    def response(self):
        return random.choice(self.nlg)


class DialogueFlow:

    def __init__(self, initial_state=None):
        self._graph = Graph()
        self._initial_state = initial_state
        self._state = self._initial_state
        self._vars = {}
        self._jump_states = {}
        self._back_states = []

    def reset(self):
        self._state = self._initial_state

    def graph(self):
        return self._graph

    def set_initial_state(self, state):
        self._initial_state = state

    def add_transition(self, source, target, nlu, nlg, settings='', nlg_vars=None):
        if self._graph.has_arc(source, target):
            self._graph.remove_arc(source, target)
        transition = DialogueTransition(source, target, nlu, nlg, settings, nlg_vars)
        self._graph.add(source, target, transition)

    def user_transition(self, utterance=None):
        best_score, next_state, vars_update = None, None, None
        for source, target, transition in self._graph.arcs_out(self._state):
            score, vars = transition.user_transition_check(utterance)
            if best_score is None or score > best_score:
                best_score, next_state, vars_update = score, target, vars
        self._vars.update(vars_update)
        self._state = next_state

    def system_transition(self):
        best_score, next_state, vars_update, utterance = None, None, None, None
        for source, target, transition in self._graph.arcs_out(self._state):
            score, vars = transition.system_transition_check()
            if best_score is None or score > best_score:
                best_score, next_state, vars_update = score, target, vars
                utterance = transition.response()
        self._vars.update(vars_update)
        self._state = next_state
        return utterance



