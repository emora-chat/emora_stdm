
import regex
import random
from structpy.automaton import StateMachine
from structpy.graph.labeled_digraph import DeterministicMapDigraph as Graph
from expression import VirtualExpression
from enum import Enum





class DialogueTransition:

    def __init__(self, knowledge_base, source, target, nlu, nlg, settings='', nlg_vars=None):
        self.source = source
        self.target = target
        self.nlu = nlu
        self.nlg = nlg
        self.nlg_vars = {} if not nlg_vars else nlg_vars
        self.settings = settings
        self.update_settings()
        self.macros = {}
        nlu, virtuals = self._process_virtuals(nlu, knowledge_base)
        self.expression = VirtualExpression(nlu, virtuals)
        self.knowledge_base = knowledge_base

    def update_settings(self):
        self.nlu_score = 10
        self.nlu_min = 1
        self.nlg_score = 10
        self.nlg_min = 1

    def user_transition_check(self, utterance, state_vars=None):
        if not self.nlu:
            return 0, {}
        else:
            match, vars = self.expression.match(utterance, state_vars)
            if match:
                return self.nlu_score, vars
            else:
                return 0, {}

    def system_transition_check(self):
        if not self.nlg:
            return 0, {}
        else:
            return self.nlg_score, self.nlg_vars

    def response(self, vars=None):
        if vars is None:
            vars = {}
        choices = []
        for choice in self.nlg:
            macro_cap = r'(\|[^|=%]+\||%[^|%=]*=\|[^|=%]+\|)'
            for macro in regex.findall(macro_cap, choice):
                var = None
                if macro[0] == '%':
                    var = macro[1:macro.find('=')]
                val = macro[macro.find('|')+1:-1]
                for x, y in vars.items():
                    val = val.replace('$' + x, y)
                travs = val.split(',')
                rings = {}
                for trav in travs:
                    negated = '-' in trav
                    chain = trav.split(':')
                    node = chain[0]
                    rings[node] = (negated, [])
                    for link in chain[1:]:
                        reversed = '/' in link
                        link = link.replace('/', '').replace('-', '')
                        rings[node][1].append((reversed, link))
                result = self.knowledge_base.attribute(rings)
                if result:
                    e = random.choice(list(result))
                    choice = choice.replace(macro, e)
                    if var:
                        vars[var] = e
            for x, y in vars.items():
                choice = choice.replace('$'+x, y)
            if '|' not in choice and '$' not in choice:
                choices.append(choice)
        return random.choice(choices)

    def _process_virtuals(self, exp, knowledge_base):
        if not exp:
            return '', {}
        i = 0
        virtuals = {}
        ont_regex = r'[^&]*(?:(&[a-zA-Z 0-9_]+)[^&]*)'
        for ont_entry in regex.findall(ont_regex, exp):
            ont_var = r'_O{}_{}'.format(str(i), ont_entry[1:])
            i += 1
            exp = exp.replace(ont_entry, ont_var)
            virtuals[ont_var] = lambda item: ont_entry[1:] in knowledge_base.types(item)
        '''
        i = 0
        kno_regex = r'(?:[^:]*[\[\]()<>{},]((?:[^(){}<>\[\],:]+):(?:[^(){}<>\[\],:]+)))'
        for kno_entry in regex.findall(kno_regex, exp):
            macros[kno_entry] = r'(?P<_K_{}>{})'.format(kno_entry, r'/[a-zA-Z _0-9]+/')
        for macro, ex in macros:
            exp.replace(macro, ex)
        self.macros = macros
        '''
        return exp, virtuals


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
            score, vars = transition.user_transition_check(utterance, self._vars)
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
                utterance = transition.response(self._vars)
        self._vars.update(vars_update)
        self._state = next_state
        return utterance



