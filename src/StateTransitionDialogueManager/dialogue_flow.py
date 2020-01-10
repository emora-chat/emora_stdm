from structpy.graph.labeled_digraph import MapMultidigraph as Graph
from src.StateTransitionDialogueManager.knowledge_base import KnowledgeBase
from src.StateTransitionDialogueManager.utilities import all_grams, random_choice
from src.StateTransitionDialogueManager.dialogue_transition import DialogueTransition


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

    def update_vars(self, vars):
        self._vars.update(vars)

    def state(self):
        return self._state

    def knowledge_base(self):
        return self._kb

    def reset(self):
        self._state = self._initial_state

    def start_module(self, state, vars=None):
        self._state = state
        if vars:
            self._vars.update(vars)

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


