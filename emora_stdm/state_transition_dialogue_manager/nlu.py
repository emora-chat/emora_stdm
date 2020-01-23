
from emora_stdm.state_transition_dialogue_manager.natex_nlu import NatexNLU
from emora_stdm.state_transition_dialogue_manager.dialogue_transition import DialogueTransition


class NLU(DialogueTransition):


    def __init__(self, natex=None, score=None, dialogue_flow=None):
        self._dialogue_flow = dialogue_flow

        self._natexes = self._construct_natexes(natex)
        if score is None:
            score = 0.0
        self._score = score

    def evaluate(self, natural_language):
        for natex in self._natexes:
            match = natex.match(natural_language)
            if match:
                return self._score, match.groupdict()
        return 0.0, {}

    def natexes(self):
        return self._natexes

    def score(self):
        return self._score

    def set_score(self, value):
        self._score = value

    def dialogue_flow(self):
        return self._dialogue_flow

    def _set_dialogue_flow(self, df):
        self._dialogue_flow = df

    def _construct_natexes(self, natex):
        if natex is None:
            return []
        if isinstance(natex, NatexNLU):
            return [natex]
        elif isinstance(natex, str):
            return [NatexNLU(natex)]
        elif isinstance(natex, list):
            for i, natex_option in enumerate(natex):
                if isinstance(natex_option, str):
                    natex[i] = NatexNLU(natex_option)
            return natex
        else:
            raise ValueError(
                'Could not construct natex list from {}'.format(natex))

    def __str__(self):
        s = 'Nlu({})'.format(
            ', '.join([x.expression() for x in self._natexes]))
        return s

    def __repr__(self):
        return str(self)