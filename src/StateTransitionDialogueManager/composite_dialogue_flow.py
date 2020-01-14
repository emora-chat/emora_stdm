
class CompositeDialogueFlow():

    def __init__(self, controller_init, controller_init_namespace, modules=None):
        self._controller = controller_init
        self._controller_namespace = controller_init_namespace
        if modules: # {string _namespace: DialogueFlow}
            self._modules = modules
        else:
            self._modules = {}
        self._modules[controller_init_namespace] = controller_init
        self._vars = {}

    def vars(self):
        return self._vars

    def state(self):
        return self.controller_namespace(), self.controller().state()

    def controller(self):
        return self._controller

    def controller_namespace(self):
        return self._controller_namespace

    def modules(self):
        return self._modules

    def add_module(self, dialogue_flow, namespace):
        self._modules[namespace] = dialogue_flow

    def add_transition(self, source, target, nlu, nlg, settings='', evaluation_transition=None):
        source_module_str, source_state_str = source.split(".")
        source_module_df = self.modules()[source_module_str]
        target_module_str, target_state_str = target.split(".") # todo - enforcement checking of whether _target exists has to be done here
        source_module_df.add_transition(source_state_str, target, nlu, nlg, settings, evaluation_transition)

    def user_transition(self, utterance=None):
        self.controller().update_vars(self.vars())
        score = self.controller().user_transition(utterance)
        self.update_controller()
        return score

    def system_transition(self):
        self.controller().update_vars(self.vars())
        utterance = self.controller().system_transition()
        self.update_controller()
        return utterance

    def update_controller(self):
        if "." in self.controller().state():
            module, state = self.controller().state().split(".")
            self._controller = self.modules()[module]
            self._controller_namespace = module
            self.controller().start_module(state, self.vars())