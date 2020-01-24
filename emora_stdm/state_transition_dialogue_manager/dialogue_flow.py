
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

Graph = Database(MapMultidigraph)

class Speaker(Enum):
    ERROR = -1
    SYSTEM = 0
    USER = 1

class DialogueFlow(Graph):

    Speaker = Speaker

    def __init__(self, initial_state: Enum, initial_speaker = Speaker.SYSTEM):
        Graph.__init__(self)
        self._initial_state = initial_state
        self._state = initial_state
        self._speaker = initial_speaker
        self._vars = {}
        self._macros = {}

    def system_turn(self):
        """
        an entire system turn comprising a single system utterance and
        one or more system transitions
        :return: the natural language system response
        """
        pass

    def user_turn(self, natural_language):
        """
        an entire user turn comprising one user utterance and
        one or more user transitions
        :param natural_language:
        :return: None
        """
        pass

    def system_transition(self, state: Enum =None, debugging=False):
        """
        :param state:
        :param debugging:
        :return: a <state, response> tuple representing the successor state and response
        """
        if state is None:
            state = self._state
        transition_options = {}
        for arc in self.arcs_out(state):
            arc_data = self.arc_data(*arc)
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
        for arc in self.arcs_out(state):
            arc_data = self.arc_data(*arc)
            natex, settings = arc_data['natex'], arc_data['settings']
            vars = dict(self._vars)
            match = natex.match(natural_language, vars, self._macros, debugging)
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
        if self.has_arc(source, target, Speaker.USER):
            raise ValueError('user transition {} -> {} already exists'.format(source, target))
        if isinstance(natex_nlu, str):
            natex_nlu = NatexNLU(natex_nlu, macros=self._macros)
        elif isinstance(natex_nlu, list) or isinstance(natex_nlu, set):
            item = next(iter(natex_nlu))
            if isinstance(item, str):
                natex_nlu = NatexNLU('{' + ', '.join(natex_nlu) + '}')
            elif isinstance(item, NatexNLU):
                raise NotImplementedError()
        if not self.has_node(source):
            self.add_state(source)
        if not self.has_node(target):
            self.add_state(target)
        self.add_arc(source, target, Speaker.USER)
        arc_data = self.arc_data(source, target, Speaker.USER)
        arc_data['natex'] = natex_nlu
        transition_settings = Settings(score=1.0)
        transition_settings.update(**settings)
        arc_data['settings'] = transition_settings

    def add_system_transition(self, source: Enum, target: Enum,
                              natex_nlg: Union[str, NatexNLG, List[str]], **settings):
        if self.has_arc(source, target, Speaker.SYSTEM):
            raise ValueError('system transition {} -> {} already exists'.format(source, target))
        if isinstance(natex_nlg, str):
            natex_nlg = NatexNLG(natex_nlg, macros=self._macros)
        elif isinstance(natex_nlg, list) or isinstance(natex_nlg, set):
            item = next(iter(natex_nlg))
            if isinstance(item, str):
                natex_nlg = NatexNLG('{' + ', '.join(natex_nlg) + '}')
            elif isinstance(item, NatexNLG):
                raise NotImplementedError()
        if not self.has_node(source):
            self.add_state(source)
        if not self.has_node(target):
            self.add_state(target)
        self.add_arc(source, target, Speaker.SYSTEM)
        arc_data = self.arc_data(source, target, Speaker.SYSTEM)
        arc_data['natex'] = natex_nlg
        transition_settings = Settings(score=1.0)
        transition_settings.update(**settings)
        arc_data['settings'] = transition_settings

    def add_state(self, state: Enum, error_successor: Union[Enum, None] =None, **settings):
        if self.has_node(state):
            raise ValueError('state {} already exists'.format(state))
        if error_successor is None:
            error_successor = self._initial_state
        state_settings = Settings()
        state_settings.update(**settings)
        self.add_node(state)
        self.data(state)['settings'] = state_settings
        self.data(state)['error'] = error_successor

    def transition_natex(self, source: Enum, target: Enum, speaker: Enum):
        return self.arc_data(source, target, speaker)['natex']

    def transition_settings(self, source: Enum, target: Enum, speaker: Enum):
        return self.arc_data(source, target, speaker)['settings']

    def state_settings(self, state: Enum):
        return self.data(state)['settings']

    def state(self):
        return self._state

    def set_state(self, state: Enum):
        self._state = state

    def speaker(self):
        return self._speaker





