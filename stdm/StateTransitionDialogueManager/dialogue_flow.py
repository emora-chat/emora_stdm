from structpy.graph.labeled_digraph import MapMultidigraph as Graph
from emora_stdm import KnowledgeBase
from emora_stdm import all_grams, random_choice
from emora_stdm import DialogueTransition
from emora_stdm import MissingStateException,\
    MissingOntologyException, MissingKnowledgeException, MissingErrorStateException
from copy import deepcopy
import regex, json
from collections import defaultdict

class DialogueFlow:

    def __init__(self, initial_state=None, name=None):
        self._graph = Graph()
        self._kb = KnowledgeBase()
        self._initial_state = initial_state
        self._state = self._initial_state
        self._vars = {}
        self._state_update_functions = {}
        self._state_selection_functions = {}
        self._jump_states = {}
        self._back_states = []
        self._nlu_multihop = set()
        self._nlg_multihop = set()
        self._original_state_transition_scores_json = None
        self._name = name

    def finalize(self):
        print("finalizing dialogue flow... ", self._name)
        self._original_state_transition_scores_json = self.nlg_transition_scores_to_json_string()

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
        self.load_nlg_transition_scores(self._original_state_transition_scores_json)
        self._vars = {}

    def graph(self):
        return self._graph

    def get_transition(self, source, target):
        return list(self.graph().label(source, target))[0]

    def set_initial_state(self, state):
        self._initial_state = state

    def add_state(self, state):
        self.graph().add(state)

    def add_states(self, states):
        for state in states:
            self.add_state(state)

    def set_nlu_multihop_tag(self, state):
        self._nlu_multihop.add(state)

    def set_nlg_multihop_tag(self, state):
        self._nlg_multihop.add(state)

    def check_ontology_references_exist(self, pattern_list):
        if pattern_list:
            for pattern in pattern_list:
                ont_matches = regex.findall(DialogueTransition._ont_capture, pattern)
                for ont in ont_matches:
                    if len(self.knowledge_base().subtypes(ont)) == 0:
                        return False, ont
        return True, None

    def check_transition_valid(self, source, target, nlu, nlg):
        transition_expression = "%s -> %s" % (source, target)
        if not self.graph().has_node(source):
            raise MissingStateException('(%s): state "%s" does not exist' % (transition_expression, source))
        if not self.graph().has_node(target):
            raise MissingStateException('(%s): state "%s" does not exist' % (transition_expression, target))
        valid, missing = self.check_ontology_references_exist(nlu)
        if not valid:
            raise MissingOntologyException('(%s): %s expression is using a non-existent ontology reference "%s"' % (
            transition_expression, 'nlu', missing))
        for nlg_expression in nlg:
            valid, missing = self.check_ontology_references_exist(nlg_expression)
            if not valid:
                raise MissingOntologyException('(%s): nlg option "%s" is using a non-existent ontology reference "%s"' % (
                    transition_expression, nlg_expression, missing))

    def add_transition(self, source, target, nlu, nlg, settings='',evaluation_function=None,selection_function=None):
        self.check_transition_valid(source, target, nlu, nlg)
        if self._graph.has_arc(source, target):
            self._graph.remove_arc(source, target)
        transition = DialogueTransition(self, source, target, nlu, nlg, settings, evaluation_function, selection_function)
        self._graph.add(source, target, transition)

    def add_state_selection_function(self, state_name, function):
        if not self.graph().has_node(state_name):
            raise MissingStateException('You are trying to add function "%s" to state "%s" and the state does not exist'%(function.__name__,state_name))
        self._state_selection_functions[state_name] = function

    def _default_state_selection(self, utterance, graph_arcs):
        best_transition, best_score, next_state, vars_update = None, None, None, None
        for source, target, transition in graph_arcs:
            score, vars = transition.eval_user_transition(utterance, self._vars)
            if best_score is None or score > best_score:
                best_transition, best_score, next_state, vars_update = transition, score, target, vars
        return best_transition, best_score, next_state, vars_update

    def set_transition_nlg_score(self, source, target, score):
        self._graph.arc(source, target).nlg_score = score

    def user_transition(self, utterance=None):
        graph_arcs = self._graph.arcs_out(self._state)
        if self._state not in self._state_selection_functions:
            transition, best_score, next_state, vars_update = self._default_state_selection(utterance, graph_arcs)
        else:
            transition, best_score, next_state, vars_update = self._state_selection_functions[self._state](self, utterance, graph_arcs)
        self._vars.update(vars_update)
        self._state = next_state
        if transition.select_function is not None:
            transition.select_function(utterance, self._state, self._vars)
        if self._state in self._state_update_functions:
            self._state_update_functions[self._state](self)
        return best_score

    def _onehop_system_transition(self):
        class Dict(dict):
            def __hash__(self):
                return hash(id(self))
        choices = {}
        utterance = ''
        for source, target, transition in self._graph.arcs_out(self._state):
            score, utterance, vars = transition.eval_system_transition(self._vars)
            choices[(transition, utterance, Dict(vars), target)] = score
        chosen = random_choice(choices)
        if chosen is not None:
            transition, utterance, vars_update, next_state = chosen[0], chosen[1], chosen[2], chosen[3]
        else:
            raise Exception("No valid system transition found")
        if transition.select_function is not None:
            transition.select_function(utterance, self._state, self._vars)
        if len(choices) > 1:  # if more than one choice, apply weighting update to reduce repetition
            if 'e' not in transition.settings():  # only do weight updating to non-error transition
                transition.downweight()
                for choice in choices:
                    if choice[0] is not transition and 'e' not in choice[0].settings():
                        choice[0].upweight()
        self._vars.update(vars_update)
        self._state = next_state
        if self._state in self._state_update_functions:
            self._state_update_functions[self._state](self)
        return utterance

    def system_transition(self):
        utterance = self._onehop_system_transition()
        while (self.state() in self._nlg_multihop):
            utterance += " " + self._onehop_system_transition()
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
        try:
            rings = self.get_kb_rings(query)
            result = self.knowledge_base().attribute(rings)
            return result
        except KeyError as e:
            raise MissingKnowledgeException("Executing query '%s' failed because %s does not exist in knowledge base"%(query,str(e).replace("KeyError: ","")))

    def add_module(self, module, namespace):
        module = deepcopy(module)
        for source, target, transition in module.graph().arcs():
            transition.set_namespace(namespace)
            transition.set_dialogue_flow(self)
            self.graph().add(transition.source(), transition.target(), transition)
        for source, target, relation in module.knowledge_base().arcs():
            if source.startswith('&'):
                source = '&' + namespace + '.' + source[1:]
            if target.startswith('&'):
                target = '&' + namespace + '.' + target[1:]
            self.knowledge_base().add(source, target, relation)
        # .extend(jump_states) - something like this

    def check_error_transitions_complete(self):
        for node in self.graph().nodes():
            error_trans = False
            for source, target, label in self.graph().arcs_out(node):
                if label.is_error_transition():
                    error_trans = True
            if not error_trans:
                raise MissingErrorStateException('state "%s" is missing an error transition'%node)

    def run(self, external_args_dict=None):
        #self.check_error_transitions_complete() # todo - need to be able to specify user vs system states (system states dont need error transitions bc not dependent on nlu from user)

        if external_args_dict:
            self.vars().update({key: val for key, val in external_args_dict.items() if val is not None})

        i = input('U: ')
        while True:
            confidence = self.user_transition(i) / 10 - 0.3
            print(self.state(), self.vars())
            if self.state() == "end":
                break

            print('({}) '.format(confidence), self.system_transition())
            if self.state() == "end":
                print(self.state(), self.vars())
                break
            i = input('U: ')

    def nlg_transition_scores_to_json_string(self):
        transition_scores = defaultdict(dict)
        for source, target, transition in self.graph().arcs():
            transition_scores[source][target] = transition.get_nlg_score()
        return json.dumps(transition_scores)

    def load_nlg_transition_scores(self, transition_json_string):
        if transition_json_string is not None:
            transition_scores = json.loads(transition_json_string)
            for source, target, transition in self.graph().arcs():
                transition.set_nlg_score(transition_scores[source][target])
        else:
            print("WARNING: transition_json_string for load_nlg_transition_scores is None")



