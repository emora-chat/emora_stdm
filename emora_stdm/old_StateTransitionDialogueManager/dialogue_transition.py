from enum import Enum

import regex
import random
from emora_stdm.old_StateTransitionDialogueManager.expression import _ExpressionReducer, _expression_parser
from emora_stdm.old_StateTransitionDialogueManager.utilities import all_grams, random_choice


class DialogueTransitionConfiguration(Enum):
    ERROR = 0
    GLOBAL = 1


class DialogueTransition:

    _var_capture = r'\$[a-zA-Z0-9_.]+'
    _ont_capture = r'&[a-zA-Z0-9_.]+'
    _query_capture = r'#[^#]*#'
    _var_query_capture = r'\%[a-zA-Z0-9_.]+=#[^#]*#'
    _var_setting_capture = r'\%[a-zA-Z0-9_.]+'

    HIGHSCORE = 10
    LOWSCORE = 3

    UPWEIGHT = 1
    DOWNWEIGHT = 1

    def __init__(self, dialogue_flow, source, target, nlu, nlg,
                 settings='', eval_function=None, select_function=None):
        self._dialogue_flow = dialogue_flow
        self._namespace = None
        self._source = source
        self._target = target
        if isinstance(nlu, list):
            self._nlu = '{' + self._join_nlu_list(nlu) + '}'
        else:
            self._nlu = nlu
        self._nlg = self._add_nlg_options(nlg)  # dictionary of utterance: prob
        self._settings = settings
        self._re = None
        if nlu:
            #print('--NEXT--')
            #print('NLU = ', self._nlu)
            self._re_compiled = None
            self._re = self._compile_nlu(self._nlu)
            #print('RE = ', self._re)
        self._update_settings()
        self._eval_function = eval_function
        self.select_function = select_function

    def _first_char_is_not_group_specifier(self, nlu):
        return nlu.strip()[0] not in '[<{/'

    def _join_nlu_list(self, nlu_list):
        s = ""
        for nlu in nlu_list:
            if self._first_char_is_not_group_specifier(nlu):
                s += '(%s), '%nlu
            else:
                s += nlu + ', '
        return s[:-2]

    def _compile_nlu(self, nlu):
        self._re_compiled = None
        expstring = nlu
        if self._first_char_is_not_group_specifier(nlu):
            expstring = '({})'.format(nlu)
        tree = _expression_parser.parse(expstring)
        return _ExpressionReducer().transform(tree)

    def source(self):
        return self._source

    def target(self):
        return self._target

    def settings(self):
        return self._settings

    def is_error_transition(self):
        return 'e' in self.settings()

    def set_dialogue_flow(self, df):
        self._dialogue_flow = df

    def upweight(self):
        self._nlg_score += DialogueTransition.UPWEIGHT

    def downweight(self):
        self._nlg_score = 0

    def get_nlg_score(self):
        return self._nlg_score

    def set_nlg_score(self, score):
        self._nlg_score = score

    def _update_settings(self):
        if 'e' in self._settings:
            self._nlu_score = DialogueTransition.LOWSCORE
            self._nlu_min = 1
            self._nlg_score = DialogueTransition.LOWSCORE
            self._nlg_min = 0
        else:
            self._nlu_score = DialogueTransition.HIGHSCORE
            self._nlu_min = 1
            self._nlg_score = DialogueTransition.HIGHSCORE
            self._nlg_min = 1

    def _insert_namespace(self, string, namespace):
        if string:
            string = string.replace('&', '&' + self._namespace + '.')
            string = string.replace('%', '%' + self._namespace + '.')
            string = string.replace('$', '$' + self._namespace + '.')
            for query in regex.findall(DialogueTransition._query_capture, string):
                query = query.group(0)
                splitter = query.find('#') + 1
                namespaced_query = query[:splitter] + namespace + '.' + query[splitter:]
                string = string.replace(query, namespaced_query)
        return string

    def set_namespace(self, namespace):
        self._namespace = namespace
        self._source = namespace + '.' + self._source
        self._target = namespace + '.' + self._target
        self._nlu = self._insert_namespace(self._nlu, namespace)
        if self._nlu:
            self._re = self._compile_nlu(self._nlu)
        for nlg, p in self._nlg.items():
            del self._nlg[nlg]
            nlg = self._insert_namespace(nlg, namespace)
            self._nlg[nlg] = p

    def eval_user_transition(self, utterance, state_vars=None):
        score, vars = 0, {}
        if 'e' not in self._settings and self._re is not None:
            re = self._re
            # variable replacement
            re = self._variable_replacement(re, state_vars)
            # ontology query and replacement
            re = self._ontology_replacement(re, utterance)
            if re is None:
                return 0, {}
            # knowledge base query and replacement
            re = self._knowledge_replacement(re, utterance)
            if re is None:
                return 0, {}
            # actually do the match, run _eval_function if specified
            match, vars = self._match(utterance, re)
            if match:
                score = self._nlu_score
        elif 'e' in self._settings:
            score = self._nlu_score
        if self._eval_function:
            score, vars = self._eval_function(utterance, {**state_vars, **vars}, score)
        return score, vars

    def eval_system_transition(self, state_vars=None):
        if not self._nlg:
            return 0, '', {}
        else:
            score, vars = 0, {}
            choices = {}
            for choice in self._nlg:
                response = choice
                # initial variable replacement
                response = self._variable_replacement(response, state_vars)
                if response is None:
                    continue
                # ontology query and replacement
                response = self._ontology_selection(response)
                if response is None:
                    continue
                # variable with knowledge base query and replacement
                response, vars = self._variable_with_knowledge_selection(response)
                if state_vars:
                    state_vars.update(vars)
                if response is None:
                    continue
                # variable replacement after variables set during knowledge base querying
                response = self._variable_replacement(response, state_vars)
                if response is None:
                    continue
                # knowledge base query and replacement
                response = self._knowledge_selection(response)
                if response is None:
                    continue
                response = response.replace(",", "")
                if "#" not in response and "%" not in response and "$" not in response:
                    choices[response] = self._nlg[choice]
            if len(choices) == 0:
                return 0, '', vars
            return self._nlg_score, random_choice(choices), vars

    def _variable_with_knowledge_selection(self, utterance):
        vars = {}
        query_matches = regex.findall(DialogueTransition._var_query_capture, utterance)
        for query in set(query_matches):
            var = regex.match(DialogueTransition._var_setting_capture, query).group(0)
            search_specs = query.replace(var, "")[2:-1]
            query_options = self._dialogue_flow.query(search_specs, filter=utterance.split())
            if query_options:
                replacement = random.choice(list(query_options))
                utterance = utterance.replace(query, replacement)
                vars[var[1:]] = replacement
        return utterance, vars

    def _knowledge_selection(self, utterance):
        query_matches = regex.findall(DialogueTransition._query_capture, utterance)
        for query in set(query_matches):
            query_options = self._dialogue_flow.query(query[1:-1], filter=utterance.split())
            if query_options:
                replacement = random.choice(list(query_options))
                utterance = utterance.replace(query, replacement)
        return utterance

    def _ontology_selection(self, utterance):
        ont_matches = regex.findall(DialogueTransition._ont_capture, utterance)
        for ont_lookup in ont_matches:
            ont_options = self._dialogue_flow.knowledge_base().subtypes(ont_lookup.strip())
            if ont_options:
                replacement = random.choice(ont_options)
                utterance = utterance.replace(ont_lookup, replacement)
        return utterance

    def _add_nlg_options(self, nlg_collection):
        if isinstance(nlg_collection, set):
            # calculate uniform probabilities
            return {item: 1/len(nlg_collection) for item in nlg_collection}
        elif isinstance(nlg_collection, dict):
            return nlg_collection
        else:
            raise Exception('nlg specification must be a set or dictionary')

    def _match(self, text, re):
        if re is None:
            return True, {}
        expression = re
        #print(self.source(), '-', self.target(), ' ==> ', re)
        self._re_compiled = regex.compile(expression)
        match = self._re_compiled.match(text + ' ')
        if match is None or match.span()[0] == match.span()[1]:
            return None, {}
        return match, {x: y.strip() for x, y in match.groupdict().items() if y}

    def _variable_replacement(self, re, state_vars):
        var_matches = regex.findall(DialogueTransition._var_capture, re)
        for var in set(var_matches):
            var_name = var[1:]
            if var_name in state_vars:
                re = re.replace(var, state_vars[var_name])
        return re

    def _ontology_replacement(self, re, utterance):
        ont_matches = regex.findall(DialogueTransition._ont_capture, re)
        for ont_lookup in ont_matches:
            re_ont_options = self._dialogue_flow.ontology_recognize(utterance, ont_lookup.strip())
            if re_ont_options:
                replacement = '(?:{})'.format('|'.join(re_ont_options))
                re = re.replace(ont_lookup, replacement)
        return re

    def _knowledge_replacement(self, re, utterance):
        query_matches = regex.findall(DialogueTransition._query_capture, re)
        for query in set(query_matches):
            query_options = self._dialogue_flow.query(query[1:-1], filter=utterance.split())
            if query_options:
                replacement = '(?:{})'.format('|'.join(query_options))
                re = re.replace(query, replacement)
        return re


