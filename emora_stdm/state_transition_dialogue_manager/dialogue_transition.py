
from abc import ABC, abstractmethod


class DialogueTransition(ABC):

    @abstractmethod
    def evaluate(self, natural_language):
        pass

    @abstractmethod
    def score(self):
        pass

    @abstractmethod
    def set_score(self, value):
        pass

    @abstractmethod
    def _set_dialogue_flow(self, df):
        pass
