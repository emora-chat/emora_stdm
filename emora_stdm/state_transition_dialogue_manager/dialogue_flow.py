
from enum import Enum
from emora_stdm.state_transition_dialogue_manager.natex_nlu import NatexNLU
from emora_stdm.state_transition_dialogue_manager.natex_nlg import NatexNLG
from structpy.graph.labeled_digraph import MapMultidigraph
from structpy.graph import Database
from typing import Union, Set, List, Dict, Callable, Tuple, NoReturn

from emora_stdm.state_transition_dialogue_manager.ngrams import Ngrams
from emora_stdm.state_transition_dialogue_manager.settings import Settings
from emora_stdm.state_transition_dialogue_manager.stochastic_options import StochasticOptions
from emora_stdm.state_transition_dialogue_manager.utilities import HashableDict
from emora_stdm.state_transition_dialogue_manager.macro import Macro

Graph = Database(MapMultidigraph)

class Speaker(Enum):
    SYSTEM = 0
    USER = 1


class DialogueFlow:

    Speaker = Speaker

    def __init__(self, initial_state: Enum, initial_speaker = Speaker.SYSTEM, macros: Dict[str, Macro] =None):
        self._graph = Graph()
        self._initial_state = initial_state
        self._state = initial_state
        self._speaker = initial_speaker
        self._vars = {}
        if macros is None:
            macros = {}
        self._macros = macros

    def run(self, debugging=False):
        """
        test in interactive mode
        :return: None
        """
        while True:
            if self.speaker() == Speaker.SYSTEM:
                print("S:", self.system_turn(debugging=debugging))
            else:
                user_input = input("U: ")
                self.user_turn(user_input, debugging=debugging)

    def system_turn(self, debugging=False):
        """
        an entire system turn comprising a single system utterance and
        one or more system transitions
        :return: the natural language system response
        """
        response, next_state = self.system_transition(debugging=debugging)
        print('Transitioning {} -> {}'.format(self._state, next_state))
        self.set_state(next_state)
        self.set_speaker(Speaker.USER)
        return response

    def user_turn(self, natural_language, debugging=False):
        """
        an entire user turn comprising one user utterance and
        one or more user transitions
        :param natural_language:
        :param debugging:
        :return: None
        """
        next_state = self.user_transition(natural_language, debugging=debugging)
        if next_state:
            print('Transitioning {} -> {}'.format(self._state, next_state))
            self.set_state(next_state)
        else:
            next_state = self._graph.data(self._state)['error']
            print('Error transition {} -> {}'.format(self._state, next_state))
            self.set_state(next_state)
        self.set_speaker(Speaker.SYSTEM)

    def system_transition(self, state: Enum =None, debugging=False):
        """
        :param state:
        :param debugging:
        :return: a <state, response> tuple representing the successor state and response
        """
        if state is None:
            state = self._state
        transition_options = {}
        for arc in self._graph.arcs_out(state):
            arc_data = self._graph.arc_data(*arc)
            natex, settings = arc_data['natex'], arc_data['settings']
            vars = HashableDict(self._vars)
            generation = natex.generate(vars=vars, macros=self._macros, debugging=debugging)
            if generation:
                transition_options[(generation, arc, vars)] = settings.score
        if transition_options:
            options = StochasticOptions(transition_options)
            response, arc, vars = options.select()
            self._vars.update(vars)
            return response, arc[1]
        else:
            raise AssertionError('dialogue flow system transition found no valid options')

    def user_transition(self, natural_language: str, state: Enum =None, debugging=False):
        """
        :param state:
        :param natural_language:
        :param debugging:
        :return: the successor state representing the highest score user transition
                 that matches natural_language, or None if none match
        """
        if state is None:
            state = self._state
        transition_options = []
        ngrams = Ngrams(natural_language, n=10)
        for arc in self._graph.arcs_out(state):
            arc_data = self._graph.arc_data(*arc)
            natex, settings = arc_data['natex'], arc_data['settings']
            vars = dict(self._vars)
            match = natex.match(natural_language, vars, self._macros, ngrams, debugging)
            if match:
                transition_options.append((settings.score, arc, vars))
        if transition_options:
            score, arc, vars = max(transition_options)
            self._vars.update(vars)
            return arc[1]
        else:
            return None

    def add_user_transition(self, source: Enum, target: Enum,
                            natex_nlu: Union[str, NatexNLU, List[str]], **settings):
        if self._graph.has_arc(source, target, Speaker.USER):
            raise ValueError('user transition {} -> {} already exists'.format(source, target))
        if isinstance(natex_nlu, str):
            natex_nlu = NatexNLU(natex_nlu, macros=self._macros)
        elif isinstance(natex_nlu, list) or isinstance(natex_nlu, set):
            item = next(iter(natex_nlu))
            if isinstance(item, str):
                natex_nlu = NatexNLU('{' + ', '.join(natex_nlu) + '}')
            elif isinstance(item, NatexNLU):
                raise NotImplementedError()
        if not self._graph.has_node(source):
            self.add_state(source)
        if not self._graph.has_node(target):
            self.add_state(target)
        self._graph.add_arc(source, target, Speaker.USER)
        arc_data = self._graph.arc_data(source, target, Speaker.USER)
        arc_data['natex'] = natex_nlu
        transition_settings = Settings(score=1.0)
        transition_settings.update(**settings)
        arc_data['settings'] = transition_settings

    def add_system_transition(self, source: Enum, target: Enum,
                              natex_nlg: Union[str, NatexNLG, List[str]], **settings):
        if self._graph.has_arc(source, target, Speaker.SYSTEM):
            raise ValueError('system transition {} -> {} already exists'.format(source, target))
        if isinstance(natex_nlg, str):
            natex_nlg = NatexNLG(natex_nlg, macros=self._macros)
        elif isinstance(natex_nlg, list) or isinstance(natex_nlg, set):
            item = next(iter(natex_nlg))
            if isinstance(item, str):
                natex_nlg = NatexNLG('{' + ', '.join(natex_nlg) + '}')
            elif isinstance(item, NatexNLG):
                raise NotImplementedError()
        if not self._graph.has_node(source):
            self.add_state(source)
        if not self._graph.has_node(target):
            self.add_state(target)
        self._graph.add_arc(source, target, Speaker.SYSTEM)
        arc_data = self._graph.arc_data(source, target, Speaker.SYSTEM)
        arc_data['natex'] = natex_nlg
        transition_settings = Settings(score=1.0)
        transition_settings.update(**settings)
        arc_data['settings'] = transition_settings

    def add_state(self, state: Enum, error_successor: Union[Enum, None] =None, **settings):
        if self._graph.has_node(state):
            raise ValueError('state {} already exists'.format(state))
        state_settings = Settings()
        state_settings.update(**settings)
        self._graph.add_node(state)
        self._graph.data(state)['settings'] = state_settings
        if error_successor is not None:
            self._graph.data(state)['error'] = error_successor

    def check(self):
        all_good = True
        for state in self._graph.nodes():
            has_system_fallback = False
            has_user_fallback = False
            for source, target, speaker in self._graph.arcs_out(state):
                if speaker == Speaker.SYSTEM:
                    if self.transition_natex(source, target, speaker).is_complete():
                        has_system_fallback = True
            data = self._graph.data(state)
            if 'error' in data:
                has_user_fallback = True
            in_labels = {x[2] for x in self._graph.arcs_in(state)}
            if Speaker.SYSTEM in in_labels:
                if not has_user_fallback:
                    print('Turn-taking dead end: state {} has no fallback user transition'.format(state))
                    all_good = False
            if Speaker.USER in in_labels:
                if not has_system_fallback:
                    print('Turn-taking dead end: state {} has no fallback system transitions'.format(state))
                    all_good = False
        return all_good


    def transition_natex(self, source: Enum, target: Enum, speaker: Enum):
        return self._graph.arc_data(source, target, speaker)['natex']

    def transition_settings(self, source: Enum, target: Enum, speaker: Enum):
        return self._graph.arc_data(source, target, speaker)['settings']

    def state_settings(self, state: Enum):
        return self._graph.data(state)['settings']

    def state(self):
        return self._state

    def set_state(self, state: Enum):
        self._state = state

    def set_error_successor(self, state, error_successor):
        self._graph.data(state)['error'] = error_successor

    def speaker(self):
        return self._speaker

    def set_speaker(self, speaker: Enum):
        self._speaker = speaker

    def graph(self):
        return self._graph





