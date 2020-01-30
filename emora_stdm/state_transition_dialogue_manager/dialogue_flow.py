
from enum import Enum

from emora_stdm.state_transition_dialogue_manager.memory import Memory
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
from emora_stdm.state_transition_dialogue_manager.knowledge_base import KnowledgeBase
from emora_stdm.state_transition_dialogue_manager.macros_common import *

Graph = Database(MapMultidigraph)

class Speaker(Enum):
    SYSTEM = 0
    USER = 1


class DialogueFlow:

    Speaker = Speaker

    def __init__(self, initial_state: Enum, states_enum=None, initial_speaker = Speaker.SYSTEM,
                 macros: Dict[str, Macro] =None, kb: KnowledgeBase =None):
        self._states_enum = states_enum
        self._graph = Graph()
        self._initial_state = self.state_enum_to_string(initial_state)
        self._state = self.state_enum_to_string(initial_state)
        self._initial_speaker = self.speaker_enum_to_string(initial_speaker)
        self._speaker = self.speaker_enum_to_string(initial_speaker)
        self._vars = {}
        if kb is None:
            kb = KnowledgeBase()
        self._kb = kb
        self._macros = {
            'ONT': ONT(self._kb)
        }
        if macros:
            self._macros.update(macros)
        self._global_states = set()

    # TOP LEVEL: SYSTEM-LEVEL USE CASES

    def run(self, debugging=False):
        """
        test in interactive mode
        :return: None
        """
        while True:
            if self.speaker() == 'SYSTEM':
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
        visited = {self.state()}
        responses = []
        while self.speaker() == 'SYSTEM':
            response, next_state = self.system_transition(debugging=debugging)
            self.take_transition(next_state)
            responses.append(response)
            if next_state in visited and self._speaker == 'SYSTEM':
                self.change_speaker()
                break
            visited.add(next_state)
        return  ' '.join(responses)

    def user_turn(self, natural_language, debugging=False):
        """
        an entire user turn comprising one user utterance and
        one or more user transitions
        :param natural_language:
        :param debugging:
        :return: None
        """
        visited = {self.state()}
        while self.speaker() == 'USER':
            next_state = self.user_transition(natural_language, debugging=debugging)
            self.take_transition(next_state)
            if next_state in visited and self._speaker == 'USER':
                self.change_speaker()
                break
            visited.add(next_state)

    # HIGH LEVEL

    def system_transition(self, state: Enum =None, debugging=False):
        """
        :param state:
        :param debugging:
        :return: a <state, response> tuple representing the successor state and response
        """
        if state is None:
            state = self._state
        transition_options = {}
        transitions = list(self.transitions(state, 'SYSTEM'))
        for transition in transitions:
            memory = self.state_settings(state).memory
            if transition not in memory or len(transitions) <= len(memory):
                natex = self.transition_natex(*transition)
                settings = self.transition_settings(*transition)
                vars = HashableDict(self._vars)
                generation = natex.generate(vars=vars, macros=self._macros, debugging=debugging)
                if generation:
                    transition_options[(generation, transition, vars)] = settings.score
        if transition_options:
            options = StochasticOptions(transition_options)
            response, transition, vars = options.select()
            self._vars.update(vars)
            next_state = transition[1]
            if debugging:
                print('Transitioning {} -> {}'.format(self.state(), next_state))
            return response, next_state
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
        for transition in self.transitions(state, 'USER'):
            natex = self.transition_natex(*transition)
            settings = self.transition_settings(*transition)
            vars = dict(self._vars)
            match = natex.match(natural_language, vars, self._macros, ngrams, debugging)
            if match:
                transition_options.append((settings.score, transition, vars))
        if transition_options:
            score, transition, vars = max(transition_options)
            self._vars.update(vars)
            next_state = transition[1]
            if debugging:
                print('Transitioning {} -> {}'.format(self.state(), next_state))
            return next_state
        else:
            next_state = self.error_successor(self.state())
            if debugging:
                print('Error transition {} -> {}'.format(self.state(), next_state))
            return next_state

    def check(self, debugging=False):
        all_good = True
        for state in self._graph.nodes():
            has_system_fallback = False
            has_user_fallback = False
            for source, target, speaker in self._graph.arcs_out(state):
                if speaker == 'SYSTEM':
                    if self.transition_natex(source, target, speaker).is_complete():
                        has_system_fallback = True
            if self.error_successor(state) is not None:
                has_user_fallback = True
            in_labels = {x[2] for x in self.incoming_transitions(state)}
            if 'SYSTEM' in in_labels:
                if not has_user_fallback:
                    if debugging:
                        print('WARNING: Turn-taking dead end: state {} has no fallback user transition'.format(state))
                    all_good = False
            if 'USER' in in_labels:
                if not has_system_fallback:
                    if debugging:
                        print('WARNING: Turn-taking dead end: state {} may have no fallback system transitions'.format(state))
                    all_good = False
        return all_good

    def add_user_transition(self, source: Enum, target: Enum,
                            natex_nlu: Union[str, NatexNLU, List[str]], **settings):
        source = self.state_enum_to_string(source)
        target = self.state_enum_to_string(target)

        if self.has_transition(source, target, 'USER'):
            if self.transition_global_nlu(source, target):
                self.remove_transition(source, target, 'USER')
            else:
                raise ValueError('user transition {} -> {} already exists'.format(source, target))
        natex_nlu = NatexNLU(natex_nlu, macros=self._macros)
        if not self.has_state(source):
            self.add_state(source)
        if not self.has_state(target):
            self.add_state(target)
        self._graph.add_arc(source, target, 'USER')
        self.set_transition_natex(source, target, 'USER', natex_nlu)
        transition_settings = Settings(score=1.0)
        transition_settings.update(**settings)
        self.set_transition_settings(source, target, 'USER', transition_settings)

    def add_system_transition(self, source: Enum, target: Enum,
                              natex_nlg: Union[str, NatexNLG, List[str]], **settings):
        source = self.state_enum_to_string(source)
        target = self.state_enum_to_string(target)

        if self.has_transition(source, target, 'SYSTEM'):
            raise ValueError('system transition {} -> {} already exists'.format(source, target))
        natex_nlg = NatexNLG(natex_nlg, macros=self._macros)
        if not self.has_state(source):
            self.add_state(source)
        if not self.has_state(target):
            self.add_state(target)
        self._graph.add_arc(source, target, 'SYSTEM')
        self.set_transition_natex(source, target, 'SYSTEM', natex_nlg)
        transition_settings = Settings(score=1.0)
        transition_settings.update(**settings)
        self.set_transition_settings(source, target, 'SYSTEM', transition_settings)

    def add_state(self, state: Enum, error_successor: Union[Enum, None] =None, **settings):
        state = self.state_enum_to_string(state)

        if self.has_state(state):
            raise ValueError('state {} already exists'.format(state))
        state_settings = Settings(user_multi_hop=False, system_multi_hop=False, global_nlu=None, memory=1)
        state_settings.update(**settings)
        self._graph.add_node(state)
        self.update_state_settings(state, **state_settings)
        if error_successor is not None:
            error_successor = self.state_enum_to_string(error_successor)
            self.set_error_successor(state, error_successor)
        for global_target in self._global_states:
            if not self.has_transition(state, global_target, 'USER'):
                self.add_user_transition(state, global_target, self.state_settings(global_target).global_nlu)
                self.set_transition_global(state, global_target, is_global=True)
    # MID LEVEL

    def take_transition(self, target):
        if self.speaker() == 'SYSTEM':
            transition = (self.state(), target, self.speaker())
            self.state_settings(self.state()).memory.add(transition)
        self.set_state(target)
        if self.speaker() == 'SYSTEM':
            if not self.state_settings(self.state()).system_multi_hop:
                self.set_speaker('USER')
        else:
            if not self.state_settings(self.state()).user_multi_hop:
                self.set_speaker('SYSTEM')

    # LOW LEVEL: PROPERTIES, GETTERS, SETTERS

    def transition_natex(self, source: Enum, target: Enum, speaker):
        source = self.state_enum_to_string(source)
        target = self.state_enum_to_string(target)
        return self._graph.arc_data(source, target, speaker)['natex']

    def set_transition_natex(self, source, target, speaker, natex):
        source = self.state_enum_to_string(source)
        target = self.state_enum_to_string(target)
        self._graph.arc_data(source, target, speaker)['natex'] = natex

    def transition_settings(self, source: Enum, target: Enum, speaker: Enum):
        source = self.state_enum_to_string(source)
        target = self.state_enum_to_string(target)
        return self._graph.arc_data(source, target, speaker)['settings']

    def set_transition_settings(self, source, target, speaker, settings):
        source = self.state_enum_to_string(source)
        target = self.state_enum_to_string(target)
        self._graph.arc_data(source, target, speaker)['settings'] = settings

    def update_transition_settings(self, source, target, speaker, **settings):
        source = self.state_enum_to_string(source)
        target = self.state_enum_to_string(target)
        self.transition_settings(source, target, speaker).update(settings)

    def transition_global_nlu(self, source: Enum, target: Enum):
        source = self.state_enum_to_string(source)
        target = self.state_enum_to_string(target)
        if self.has_transition(source, target, 'USER') \
        and 'global' in self._graph.arc_data(source, target, 'USER'):
            return self._graph.arc_data(source, target, 'USER')['global']
        return False

    def set_transition_global(self, source, target, is_global):
        source = self.state_enum_to_string(source)
        target = self.state_enum_to_string(target)
        self._graph.arc_data(source, target, 'USER')['global'] = is_global

    def state_settings(self, state: Enum):
        return self._graph.data(state)['settings']

    def _update_global_states(self, state):
        global_nlu = self.state_settings(state).global_nlu
        if global_nlu:
            self._global_states.add(state)
            for source in self.states():
                if source is not state and not self.has_transition(source, state, 'USER'):
                    self.add_user_transition(source, state, global_nlu)
                    self.set_transition_global(source, state, is_global=True)
        else:
            if state in self._global_states:
                self._global_states.remove(state)
                for source in self.states():
                    for transition in list(self.transitions(source)):
                        if self.transition_global_nlu(*transition):
                            self.remove_transition(*transition)

    def update_state_settings(self, state, **settings):
        if 'settings' not in self._graph.data(state):
            self._graph.data(state)['settings'] = Settings()
        if 'memory' in settings:
            settings['memory'] = Memory(settings['memory'])
        self.state_settings(state).update(**settings)
        self._update_global_states(state)

    def remove_transition(self, source, target, speaker):
        MapMultidigraph.remove_arc(self.graph(), source, target, speaker)

    def states(self):
        return self.graph().nodes()

    def state(self):
        return self._state

    def set_state(self, state: Enum):
        if isinstance(state, Enum):
            self._state = self.state_enum_to_string(state)
        elif isinstance(state, str):
            self._state = state
        else:
            raise Exception("Unidentified state argument: should be string or programmer-defined Enum value")

    def has_state(self, state):
        if isinstance(state, Enum):
            return self._graph.has_node(self.state_enum_to_string(state))
        elif isinstance(state, str):
            return self._graph.has_node(state)
        else:
            raise Exception("Unidentified state argument: should be string or programmer-defined Enum value")

    def error_successor(self, state):
        data = self._graph.data(state)
        if 'error' in data:
            return data['error']
        else:
            return None

    def set_error_successor(self, state, error_successor):
        self._graph.data(state)['error'] = error_successor

    def speaker(self):
        return self._speaker

    def set_speaker(self, speaker: Union[str, Enum]):
        if isinstance(speaker, Enum):
            self._speaker = self.speaker_enum_to_string(speaker)
        elif isinstance(speaker, str):
            self._speaker = speaker
        else:
            raise Exception("Unidentified speaker argument: should be string or Speaker Enum value")

    def graph(self):
        return self._graph

    def state_enum_to_string(self, enum):
        if isinstance(enum, Enum):
            if self._states_enum is not None:
                return self._states_enum(enum).name
            else:
                raise Exception("You are missing the States Enum class as "
                                "a parameter to the DialogueFlow constructor")
        else:
            if not isinstance(enum, str):
                raise Exception("You are not using string state values, so you must pass the States Enum class as "
                                "a parameter to the DialogueFlow constructor")
            return enum

    def speaker_enum_to_string(self, enum):
        return Speaker(enum).name

    def transitions(self, source_state, speaker=None):
        """
        get (source, target, speaker) transition tuples for the entire state machine
        (default) or that lead out from a given source_state
        :param source_state: optionally, filter returned transitions by source state
        :param speaker: optionally, filter returned transitions by speaker
        :return: a generator over (source, target, speaker) 3-tuples
        """
        if speaker is None:
            yield from self._graph.arcs_out(source_state)
        elif self._graph.has_arc_label(source_state, speaker):
            yield from self._graph.arcs_out(source_state, label=speaker)
        else:
            return

    def has_transition(self, source, target, speaker):
        return self._graph.has_arc(source, target, speaker)

    def incoming_transitions(self, target_state):
        yield from self._graph.arcs_in(target_state)

    def change_speaker(self):
        if self.speaker() == 'USER':
            self.set_speaker('SYSTEM')
        elif self.Speaker == 'SYSTEM':
            self.set_speaker('USER')

    def reset(self):
        self._state = self._initial_state
        self._speaker = self._initial_speaker
        self._vars = {}
        for state in self.graph().nodes():
            self.state_settings(state).memory.clear()
