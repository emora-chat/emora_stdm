
from abc import ABC, abstractmethod, abstractproperty
from emora_stdm.state_transition_dialogue_manager.ngrams import Ngrams
from typing import Union, Set, List, Dict, Callable, Tuple, NoReturn, Any


class Macro(ABC):

    @abstractmethod
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        pass

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

