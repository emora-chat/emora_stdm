
from enum import Enum
from emora_stdm.state_transition_dialogue_manager.natex_nlu import NatexNLU
from emora_stdm.state_transition_dialogue_manager.natex_nlg import NatexNLG
from structpy.graph.labeled_digraph import MapMultidigraph
from structpy.graph import Database

from emora_stdm.state_transition_dialogue_manager.ngrams import Ngrams
from emora_stdm.state_transition_dialogue_manager.settings import Settings
from emora_stdm.state_transition_dialogue_manager.stochastic_options import StochasticOptions

Graph = Database(MapMultidigraph)

class Speaker(Enum):
    ERROR = -1
    SYSTEM = 0
    USER = 1

class DialogueFlow(Graph):

    def __init__(self, initial_state: str, initial_speaker = Speaker.SYSTEM):
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

    def system_transition(self, state, debugging=False):
        """
        :param state:
        :param debugging:
        :return: a <state, response> tuple representing the successor state and response
        """
        transition_options = {}
        for arc in self.arcs_out(state):
            arc_data = self.arc_data(*arc)
            natex, settings = arc_data['natex'], arc_data['settings']
            vars = dict(self._vars)
            generation = natex.generate(vars=vars, macros=self._macros, debugging=debugging)
            transition_options[generation] = settings.score
            if generation:
                transition_options[(generation, arc, vars)] = settings.score
        if transition_options:
            options = StochasticOptions(transition_options)
            response, arc, vars = options.select()
            self._vars.update(vars)
            return arc[1], response
        else:
            raise AssertionError('dialogue flow system transition found no valid options')

    def user_transition(self, state, natural_language, debugging=False):
        """
        :param state:
        :param natural_language:
        :param debugging:
        :return: the successor state representing the highest score user transition
                 that matches natural_language, or None if none match
        """
        transition_options = []
        ngrams = Ngrams(natural_language, n=10)
        for arc in self.arcs_out(state):
            arc_data = self.arc_data(*arc)
            natex, settings = arc_data['natex'], arc_data['settings']
            vars = dict(self._vars)
            natex.compile(ngrams, vars, self._macros, debugging)
            match = natex.match(natural_language, vars, self._macros, debugging)
            if match:
                transition_options.append((settings.score, arc, vars))
        if transition_options:
            score, arc, vars = max(transition_options)
            self._vars.update(vars)
            return arc[1]
        else:
            return None

    def add_user_transition(self, source, target, natex_nlu, **settings):
        if self.has_arc(source, target, Speaker.USER):
            raise ValueError('user transition {} -> {} already exists'.format(source, target))
        self.add_arc(source, target, Speaker.USER)
        arc_data = self.arc_data(source, target, Speaker.USER)
        arc_data['natex_nlu'] = NatexNLU(natex_nlu, macros=self._macros)
        transition_settings = Settings(score=1.0)
        transition_settings.update(**settings)
        arc_data['settings'] = transition_settings

    def add_system_transition(self, source, target, natex_nlg, **settings):
        if self.has_arc(source, target, Speaker.SYSTEM):
            raise ValueError('system transition {} -> {} already exists'.format(source, target))
        self.add_arc(source, target, Speaker.SYSTEM)
        arc_data = self.arc_data(source, target, Speaker.SYSTEM)
        arc_data['natex_nlg'] = NatexNLG(natex_nlg, macros=self._macros)
        transition_settings = Settings(score=1.0)
        transition_settings.update(**settings)
        arc_data['settings'] = transition_settings

    def add_state(self, state, error_successor=None, **settings):
        if self.has_node(state):
            raise ValueError('state {} already exists'.format(state))
        if error_successor is None:
            error_successor = self._initial_state
        state_settings = Settings()
        state_settings.update(**settings)
        self.add_node(state)
        self.data(state)['settings'] = state_settings
        self.data(state)['error'] = error_successor

    def transition_natex(self, source, target, speaker):
        return self.arc_data(source, target, speaker)['natex']

    def transition_settings(self, source, target, speaker):
        return self.arc_data(source, target, speaker)['settings']






