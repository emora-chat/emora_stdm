
from emora_stdm.state_transition_dialogue_manager.macro import Macro
from emora_stdm.state_transition_dialogue_manager.ngrams import Ngrams
from typing import Union, Set, List, Dict, Callable, Tuple, NoReturn, Any



class ONT(Macro):
    def __init__(self, kb):
        self.kb = kb
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        node = args[0]
        return self.kb.expressions(self.kb.subtypes(node))
