
from emora_stdm.state_transition_dialogue_manager.dialogue_flow import DialogueFlow
from emora_stdm.state_transition_dialogue_manager.macros_common import *
from emora_stdm.state_transition_dialogue_manager.knowledge_base import KnowledgeBase
from time import time
import dill
from pathos.multiprocessing import ProcessingPool as Pool

def precache(transition_datas):
    for tran_datas in transition_datas:
        tran_datas['natex'].precache()
    parsed_trees = [x['natex']._compiler._parsed_tree for x in transition_datas]
    return parsed_trees

class CompositeDialogueFlow:

    def __init__(self, initial_state, system_error_state, user_error_state,
                 initial_speaker = None, macros=None, kb=None):
        if isinstance(system_error_state, str):
            system_error_state = ('SYSTEM', system_error_state)
        if isinstance(user_error_state, str):
            user_error_state = ('SYSTEM', user_error_state)
        # the dialogue flow currently controlling the conversation
        self._controller = DialogueFlow(initial_state, initial_speaker, macros, kb)
        self._controller_name = 'SYSTEM'
        # namespace : dialogue flow mapping
        self._components = {'SYSTEM': self._controller}
        self._system_error_state = system_error_state
        self._user_error_state = user_error_state

    def run(self, debugging=False):
        """
        test in interactive mode
        :return: None
        """
        while True:
            if self._controller.speaker() == DialogueFlow.Speaker.SYSTEM:
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
        visited = {self._controller.state()}
        responses = []
        while self._controller.speaker() is DialogueFlow.Speaker.SYSTEM:
            try:
                response, next_state = self._controller.system_transition(self._controller.state(), debugging=debugging)
                self._controller.take_transition(next_state)
            except Exception as e:
                print('Error in CompositeDialogueFlow. Component: {}  State: {}'.format(self._controller_name, self._controller.state()))
                print(e)
                response, next_state = '', self._system_error_state
                visited = visited - {next_state}
            if isinstance(next_state, tuple):
                self.set_control(*next_state)
            responses.append(response)
            if next_state in visited and self._controller._speaker is DialogueFlow.Speaker.SYSTEM:
                self._controller.change_speaker()
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
        visited = {self._controller.state()}
        while self._controller.speaker() is DialogueFlow.Speaker.USER:
            try:
                next_state = self._controller.user_transition(natural_language, self._controller.state(), debugging=debugging)
                self._controller.take_transition(next_state)
            except Exception as e:
                print('Error in CompositeDialogueFlow. Component: {}  State: {}'.format(self._controller_name, self._controller.state()))
                print(e)
                next_state = self._user_error_state
            if isinstance(next_state, tuple):
                self.set_control(*next_state)
            if next_state in visited and self._controller._speaker is DialogueFlow.Speaker.USER:
                self._controller.change_speaker()
                break
            visited.add(next_state)

    def set_control(self, namespace, state):
        speaker = self._controller.speaker()
        self.set_controller(namespace)
        self._controller.set_speaker(speaker)
        self._controller.set_state(state)

    def precache_transitions(self, process_num=1):
        start = time()

        transition_data_sets = []
        for i in range(process_num):
            transition_data_sets.append([])
        count = 0

        if process_num == 1:
            for name,df in self._components.items():
                for transition in df._graph.arcs():
                    data = df._graph.arc_data(*transition)
                    data['natex'].precache()
        else:
            for name,df in self._components.items():
                for transition in df._graph.arcs():
                    transition_data_sets[count].append(df._graph.arc_data(*transition))
                    count = (count + 1) % process_num

            print("multiprocessing...")
            p = Pool(process_num)
            results = p.map(precache, transition_data_sets)
            for i in range(len(results)):
                result_list = results[i]
                t_list = transition_data_sets[i]
                for j in range(len(result_list)):
                    parsed_tree = result_list[j]
                    t = t_list[j]
                    t['natex']._compiler._parsed_tree = parsed_tree

        print("Elapsed: ", time() - start)

    def add_state(self, state, error_successor=None):
        if isinstance(state, tuple):
            ns, state = state
        else:
            ns = 'SYSTEM'
        self._components[ns].add_state(state, error_successor)

    def add_user_transition(self, source, target, natex_nlu, **settings):
        if isinstance(source, tuple):
            ns, source = source
        else:
            ns = 'SYSTEM'
        self._components[ns].add_user_transition(source, target, natex_nlu, **settings)

    def add_system_transition(self, source, target, natex_nlg, **settings):
        if isinstance(source, tuple):
            ns, source = source
        else:
            ns = 'SYSTEM'
        self._components[ns].add_system_transition(source, target, natex_nlg, **settings)

    def add_component(self, component, namespace):
        self._components[namespace] = component

    def component(self, namespace):
        return self._components[namespace]

    def set_state(self, state):
        self._controller.set_state(state)

    def set_controller(self, controller_name):
        old_controller_vars = self._controller.vars()
        self._controller = self.component(controller_name)
        self._controller_name = controller_name
        new_controller_vars = self._controller.vars()
        new_controller_vars.update(old_controller_vars)
        self._controller.set_vars(new_controller_vars)

    def set_vars(self, vars):
        self._controller.set_vars(vars)

    def reset(self):
        for name,component in self._components.items():
            component.reset()
        self.set_controller("SYSTEM")

    def controller(self):
        return self._controller

    def controller_name(self):
        return self._controller_name

    def state(self):
        return self._controller_name, self._controller.state()
