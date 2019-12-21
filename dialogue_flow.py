
import regex
import random
from structpy.automaton import StateMachine
from structpy.graph.labeled_digraph import MapMultidigraph as Graph
from knowledge_base import KnowledgeBase
from expression import VirtualExpression
from enum import Enum

HIGHSCORE = 10
LOWSCORE = 3

_macro_cap = r'(\|[^|=%]+\||%[^|%=]*=\|[^|=%]+\|)'
_nlu_macro_cap = r'(\|[^|=%]+\|)'

def random_choice(choices):
    transitions = list(choices.keys())
    total = sum(choices.values())
    thresholds = []
    curr = 0
    for t in transitions:
        prob = choices[t] / total
        curr += prob
        thresholds.append(curr)
    r = random.uniform(0, 1.0)
    for i, threshold in enumerate(thresholds):
        if r < threshold:
            return transitions[i]
    return transitions[-1]

def get_kb_rings(re, macro, vars):
    var = None
    if macro[0] == '%':
        var = macro[1:macro.find('=')]
    val = macro[macro.find('|') + 1:-1]
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
    return rings, var


class DialogueTransition:

    def __init__(self, knowledge_base, source, target, nlu, nlg, evaluation_transition=None, settings='', nlg_vars=None):
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
        self.evaluate_transition = evaluation_transition
        self.knowledge_base = knowledge_base

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

    def user_transition_check(self, utterance, state_vars=None, arg_dict=None):
        score, vars = self._user_transition_check(utterance, state_vars)
        if self.evaluate_transition:
            score, vars = self.evaluate_transition(arg_dict, score, vars)
        return score, vars

    def _user_transition_check(self, utterance, state_vars=None):
        if not self.nlu:
            return self.nlu_score, {}
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
            for macro in regex.findall(_macro_cap, choice):
                rings, var = get_kb_rings(_macro_cap, macro, vars)
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

            class ont_virtual:
                def __init__(self, ont_entry):
                    self.ont_entry = ont_entry
                def __call__(self, item, vars):
                    return knowledge_base.type_check(item, self.ont_entry[1:])

            virtuals[ont_var] = ont_virtual(ont_entry)
        i = 0
        for kb_entry in regex.findall(_nlu_macro_cap, exp):
            kb_var = r'_K{}_'.format(str(i))
            exp = exp.replace(kb_entry, kb_var)

            class kb_virtual:
                def __init__(self, kb_entry):
                    self.kb_entry = kb_entry
                def __call__(self, item, vars):
                    kb_entry = str(self.kb_entry)
                    for k, v in vars.items():
                        kb_entry = kb_entry.replace('$'+k, v)
                    rings, _ = get_kb_rings(_nlu_macro_cap, kb_entry, {})
                    return knowledge_base.valid_attribute(item, rings)

            virtuals[kb_var] = kb_virtual(kb_entry)
        return exp, virtuals


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



