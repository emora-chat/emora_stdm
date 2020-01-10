
import regex
import random
from src.StateTransitionDialogueManager.expression import _ExpressionReducer, _expression_parser
from src.StateTransitionDialogueManager.utilities import all_grams, random_choice


class DialogueTransition:

    _var_capture = r'\$[a-zA-Z 0-9_]+'
    _ont_capture = r'&[a-zA-Z 0-9_]+'
    _query_capture = r'#[^#]*#'
    _var_query_capture = r'\%[a-zA-Z 0-9_]+=#[^#]*#'
    _var_setting_capture = r'\%[a-zA-Z 0-9_]+'

    HIGHSCORE = 10
    LOWSCORE = 3

    def __init__(self, dialogue_flow, source, target, nlu, nlg,
                 settings='', eval_function=None, select_function=None):
        self.dialogue_flow = dialogue_flow
        self.source = source
        self.target = target
        self.nlu = nlu
        self.nlg = self.add_nlg_options(nlg)  # dictionary of utterance: prob
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
        self.select_function = select_function

    def update_settings(self):
        if 'e' in self.settings:
            self.nlu_score = DialogueTransition.LOWSCORE
            self.nlu_min = 1
            self.nlg_score = DialogueTransition.LOWSCORE
            self.nlg_min = 0
        else:
            self.nlu_score = DialogueTransition.HIGHSCORE
            self.nlu_min = 1
            self.nlg_score = DialogueTransition.HIGHSCORE
            self.nlg_min = 1

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
            score, vars = self.eval_function(utterance, {**state_vars, **vars}, score)
        return score, vars

    def eval_system_transition(self, state_vars=None):
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
                response = response.replace(",", "")
                if "#" not in response and "%" not in response and "$" not in response:
                    choices[response] = self.nlg[choice]
            if len(choices) == 0:
                return 0, '', vars
            return self.nlg_score, random_choice(choices), vars

    def variable_with_knowledge_selection(self, utterance):
        vars = {}
        query_matches = regex.findall(DialogueTransition._var_query_capture, utterance)
        for query in set(query_matches):
            var = regex.match(DialogueTransition._var_setting_capture, query).group(0)
            search_specs = query.replace(var, "")[2:-1]
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

    def ontology_selection(self, utterance):
        ont_matches = regex.findall(DialogueTransition._ont_capture, utterance)
        for ont_lookup in ont_matches:
            ont_options = self.dialogue_flow.knowledge_base().subtypes(ont_lookup[1:].strip())
            if ont_options:
                replacement = random.choice(ont_options)
                utterance = utterance.replace(ont_lookup, replacement)
        return utterance

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

