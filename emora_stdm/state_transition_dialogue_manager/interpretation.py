
import regex
from emora_stdm.state_transition_dialogue_manager.natex import Natex


class Interpretation:

    def __init__(self, dialogue_flow, natex=None, score=None):
        self._dialogue_flow = dialogue_flow
        if isinstance(natex, str):
            natex = Natex(natex)
        self._natex = natex
        self._score = score

    def evaluate(self, natural_language):
        if not self._natex:
            return 0.0, {}
        match = self._natex.match(natural_language)
        if not match:
            return 0.0, {}
        else:
            return self._score, match.groupdict()

    def natex(self):
        return self._natex

    def score(self):
        return self._score

    def set_score(self, value):
        self._score = value