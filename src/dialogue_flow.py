import regex
import random
from structpy.graph.labeled_digraph import MapMultidigraph as Graph
from src.knowledge_base import KnowledgeBase
from src.expression import _expression_parser, _ExpressionReducer
from src.utilities import all_grams, random_choice

HIGHSCORE = 10
LOWSCORE = 3

_macro_cap = r'(\|[^|=%]+\||%[^|%=]*=\|[^|=%]+\|)'
_nlu_macro_cap = r'(\|[^|=%]+\|)'


class DialogueTransition:

    _var_capture = r'\$[a-zA-Z 0-9_]+'
    _ont_capture = r'&[a-zA-Z 0-9_]+'
    _query_capture = r'#[^#]*#'
    _var_query_capture = r'\%[a-zA-Z 0-9_]+=#[^#]*#'
    _var_setting_capture = r'\%[a-zA-Z 0-9_]+'

    def __init__(self, dialogue_flow, source, target, nlu, nlg,
                 settings='', eval_function=None):
        self.dialogue_flow = dialogue_flow
        self.source = source
        self.target = target
        self.nlu = nlu
        self.nlg = self.add_nlg_options(nlg) # dictionary of utterance: prob
        self.settings = settings
        self.re = None
        if nlu:
            expstring = nlu
            if nlu[0] not in '-[<{/':
                expstring = '({})'.format(nlu)
            tree = _expression_parser.parse(expstring)
            self.re = _ExpressionReducer().transform(tree)
            self._re_compiled = None

        self.update_settings()
        self.eval_function = eval_function

    def add_nlg_options(self, nlg_collection):
        if isinstance(nlg_collection, set):
            # calculate uniform probabilities
            nlg_collection = {item: 1/len(nlg_collection) for item in nlg_collection}
        return nlg_collection

    def match(self, text, re):
        if re is None:
            return True, {}
        expression = re
        self._re_compiled = regex.compile(expression)
        match = self._re_compiled.match(text + ' ')
        if match is None or match.span()[0] == match.span()[1]:
            return None, {}
        return match, {x: y.strip() for x, y in match.groupdict().items() if y}

    def update_settings(self):
        if 'e' in self.settings:
            self.nlu_score = LOWSCORE
            self.nlu_min = 1
            self.nlg_score = LOWSCORE
            self.nlg_min = 0
        else:
            self.nlu_score = HIGHSCORE
            self.nlu_min = 1
            self.nlg_score = HIGHSCORE
            self.nlg_min = 1

    def variable_replacement(self, re, state_vars):
        var_matches = regex.findall(DialogueTransition._var_capture, re)
        for var in set(var_matches):
            var_name = var[1:]
            if var_name in state_vars:
                re = re.replace(var, state_vars[var_name])
        return re

    def ontology_replacement(self, re, utterance):
        ont_matches = regex.findall(DialogueTransition._ont_capture, re)
        for ont_lookup in ont_matches:
            re_ont_options = self.dialogue_flow.ontology_recognize(utterance, ont_lookup[1:].strip())
            if re_ont_options:
                replacement = '(?:{})'.format('|'.join(re_ont_options))
                re = re.replace(ont_lookup, replacement)
        return re

    def knowledge_replacement(self, re, utterance):
        query_matches = regex.findall(DialogueTransition._query_capture, re)
        for query in set(query_matches):
            query_options = self.dialogue_flow.query(query[1:-1], filter=utterance.split())
            if query_options:
                replacement = '(?:{})'.format('|'.join(query_options))
                re = re.replace(query, replacement)
        return re

    def eval_user_transition(self, utterance, state_vars=None):
        score, vars = 0, {}
        if 'e' not in self.settings and self.re is not None:
            re = self.re
            # variable replacement
            re = self.variable_replacement(re, state_vars)
            # ontology query and replacement
            re = self.ontology_replacement(re, utterance)
            if re is None:
                return 0, {}
            # knowledge base query and replacement
            re = self.knowledge_replacement(re, utterance)
            if re is None:
                return 0, {}
            # actually do the match, run eval_function if specified
            match, vars = self.match(utterance, re)
            if match:
                score = self.nlu_score
        elif 'e' in self.settings:
            score = self.nlu_score
        if self.eval_function:
            score, vars = self.eval_function(state_vars, score, vars)
        return score, vars

    def ontology_selection(self, utterance):
        ont_matches = regex.findall(DialogueTransition._ont_capture, utterance)
        for ont_lookup in ont_matches:
            ont_options = self.dialogue_flow.knowledge_base().subtypes(ont_lookup[1:].strip())
            if ont_options:
                replacement = random.choice(ont_options)
                utterance = utterance.replace(ont_lookup, replacement)
        return utterance

    def variable_with_knowledge_selection(self, utterance):
        vars = {}
        query_matches = regex.findall(DialogueTransition._var_query_capture, utterance)
        for query in set(query_matches):
            var = regex.match(DialogueTransition._var_setting_capture, query).group(0)
            search_specs = query.replace(var,"")[2:-1]
            query_options = self.dialogue_flow.query(search_specs, filter=utterance.split())
            if query_options:
                replacement = random.choice(list(query_options))
                utterance = utterance.replace(query, replacement)
                vars[var[1:]] = replacement
        return utterance, vars

    def knowledge_selection(self, utterance):
        query_matches = regex.findall(DialogueTransition._query_capture, utterance)
        for query in set(query_matches):
            query_options = self.dialogue_flow.query(query[1:-1], filter=utterance.split())
            if query_options:
                replacement = random.choice(list(query_options))
                utterance = utterance.replace(query, replacement)
        return utterance

    def eval_system_transition(self, state_vars=None, arg_dict=None):
        if not self.nlg:
            return 0, '', {}
        else:
            score, vars = 0, {}
            choices = {}
            for choice in self.nlg:
                response = choice
                # initial variable replacement
                response = self.variable_replacement(response, state_vars)
                if response is None:
                    continue
                # ontology query and replacement
                response = self.ontology_selection(response)
                if response is None:
                    continue
                # variable with knowledge base query and replacement
                response, vars = self.variable_with_knowledge_selection(response)
                if state_vars:
                    state_vars.update(vars)
                if response is None:
                    continue
                # variable replacement after variables set during knowledge base querying
                response = self.variable_replacement(response, state_vars)
                if response is None:
                    continue
                # knowledge base query and replacement
                response = self.knowledge_selection(response)
                if response is None:
                    continue
                response = response.replace(",","")
                if "#" not in response and "%" not in response and "$" not in response:
                    choices[response] = self.nlg[choice]
            if len(choices) == 0:
                return 0, '', vars
            return self.nlg_score, random_choice(choices), vars


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

    def set_vars(self, vars):
        if vars is None:
            vars = {}
        self._vars = vars

    def state(self):
        return self._state

    def knowledge_base(self):
        return self._kb

    def reset(self):
        self._state = self._initial_state

    def graph(self):
        return self._graph

    def get_transition(self, source, target):
        return list(self.graph().label(source, target))[0]

    def set_initial_state(self, state):
        self._initial_state = state

    def add_transition(self, source, target, nlu, nlg, settings='',evaluation_transition=None):
        if self._graph.has_arc(source, target):
            self._graph.remove_arc(source, target)
        transition = DialogueTransition(self, source, target, nlu, nlg, settings, evaluation_transition)
        self._graph.add(source, target, transition)

    def set_transition_nlg_score(self, source, target, score):
        self._graph.arc(source, target).nlg_score = score

    def user_transition(self, utterance=None):
        best_score, next_state, vars_update = None, None, None
        for source, target, transition in self._graph.arcs_out(self._state):
            score, vars = transition.eval_user_transition(utterance, self._vars)
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
        utterance = ''
        for source, target, transition in self._graph.arcs_out(self._state):
            score, utterance, vars = transition.eval_system_transition(self._vars)
            choices[(transition, utterance, Dict(vars), target)] = score
        transition, utterance, vars_update, next_state = random_choice(choices)
        self._vars.update(vars_update)
        self._state = next_state
        if self._state in self._state_update_functions:
            self._state_update_functions[self._state](self)
        return utterance

    def register_state_update_function(self, state, function_ptr):
        self._state_update_functions[state] = function_ptr

    def ontology_recognize(self, utterance, ontology_entry):
        subtypes = self._kb.subtypes(ontology_entry)
        all_ngrams = all_grams(utterance)
        subtypes.intersection_update(all_ngrams)
        return subtypes

    def get_kb_rings(self, query_string):
        travs = query_string.split(',')
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
        return rings

    def query(self, query, filter):
        rings = self.get_kb_rings(query)
        result = self.knowledge_base().attribute(rings)
        return result


