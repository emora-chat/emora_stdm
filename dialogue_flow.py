
import regex
import random
from structpy.automaton import StateMachine
from structpy.graph.labeled_digraph import MapMultidigraph as Graph
from knowledge_base import KnowledgeBase
from expression import Expression
from enum import Enum

HIGHSCORE = 10
LOWSCORE = 3

_macro_cap = r'(\|[^|=%]+\||%[^|%=]*=\|[^|=%]+\|)'
_nlu_macro_cap = r'(\|[^|=%]+\|)'


class DialogueTransition:

    def __init__(self, dialogue_flow, source, target, nlu, nlg,
                 settings='', eval_function=None):
        self.dialogue_flow = dialogue_flow
        self.source = source
        self.target = target
        self.nlu = Expression(nlu)
        self.nlg = nlg
        self.settings = settings

        self.update_settings()
        self.eval_function = eval_function

    def update_settings(self):
        if 'e' in self.settings:
            self.nlu_score = LOWSCORE
            self.nlu_min = 1
            self.nlg_score = 0
            self.nlg_min = 0
        else:
            self.nlu_score = HIGHSCORE
            self.nlu_min = 1
            self.nlg_score = HIGHSCORE
            self.nlg_min = 1

    def eval_user_transition(self, utterance, state_vars=None, arg_dict=None):
        score, vars = 0, {}
        match, vars = self.nlu.match(utterance, state_vars)
        if match:
            return self.nlu_score, vars
        if self.eval_function:
            score, vars = self.eval_function(arg_dict, score, vars)
        return score, vars

    def eval_system_transition(self):
        if not self.nlg:
            return 0, '', {}
        else:
            pass  # todo
            # return self.nlg_score, self.nlg_vars


class DialogueFlow:

    def __init__(self, initial_state=None):
        self._graph = Graph()
        self._kb = KnowledgeBase()
        self._initial_state = initial_state
        self._state = self._initial_state
        self._vars = {}
        self._state_update_functions = {}
        self._jump_states = {}
        self._back_states = []

    def vars(self):
        return self._vars

    def state(self):
        return self._state

    def knowledge_base(self):
        return self._kb

    def reset(self):
        self._state = self._initial_state

    def graph(self):
        return self._graph

    def set_initial_state(self, state):
        self._initial_state = state

    def add_transition(self, source, target, nlu, nlg, evaluation_transition=None, settings='', nlg_vars=None):
        if self._graph.has_arc(source, target):
            self._graph.remove_arc(source, target)
        transition = DialogueTransition(self._kb, source, target, nlu, nlg, evaluation_transition, settings, nlg_vars)
        self._graph.add(source, target, transition)

    def set_transition_nlg_score(self, source, target, score):
        self._graph.arc(source, target).nlg_score = score

    def user_transition(self, utterance=None, arg_dict=None):
        best_score, next_state, vars_update = None, None, None
        for source, target, transition in self._graph.arcs_out(self._state):
            score, vars = transition.user_transition_check(utterance, self._vars, arg_dict)
            if best_score is None or score > best_score:
                best_score, next_state, vars_update = score, target, vars
        self._vars.update(vars_update)
        self._state = next_state
        if self._state in self._state_update_functions:
            self._state_update_functions[self._state](self)
        return best_score

    def system_transition(self):
        class Dict(dict):
            def __hash__(self):
                return hash(id(self))
        choices = {}
        for source, target, transition in self._graph.arcs_out(self._state):
            score, vars = transition.system_transition_check()
            choices[(transition, Dict(vars), target)] = score
        transition, vars_update, next_state = random_choice(choices)
        utterance = transition.response(self._vars)
        self._vars.update(vars_update)
        self._state = next_state
        if self._state in self._state_update_functions:
            self._state_update_functions[self._state](self)
        return utterance

    def register_state_update_function(self, state, function_ptr):
        self._state_update_functions[state] = function_ptr



