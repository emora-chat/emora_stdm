
from emora_stdm.state_transition_dialogue_manager.dialogue_transition import DialogueTransition
from emora_stdm.state_transition_dialogue_manager.natex_nlg import NatexNLG
from emora_stdm.state_transition_dialogue_manager.stochastic_options import StochasticOptions


class NLG(DialogueTransition):

    def __init__(self, natex, score=None, dialogue_flow=None):
        self._dialogue_flow = dialogue_flow
        self._natexes = self._construct_natexes(natex)
        self._score = score

    def evaluate(self, ngrams=None, vars=None, macros=None, debugging=False):
        if not self._natexes:
            return 0.0
        else:
            response, vars = self._natexes.select().generate_with_vars(ngrams, vars, macros, debugging)
            return self._score, response, vars

    def score(self):
        return self._score

    def set_score(self, value):
        self._score = value

    def _set_dialogue_flow(self, df):
        self._dialogue_flow = df

    def _construct_natexes(self, natex):
        if isinstance(natex, str):
            return StochasticOptions([NatexNLG(natex)])
        else:
            return StochasticOptions(natex)

    def __str__(self):
        s = 'Nlg({})'.format(
            ', '.join([x.expression() for x in self._natexes]))
        return s

    def __repr__(self):
        return str(self)