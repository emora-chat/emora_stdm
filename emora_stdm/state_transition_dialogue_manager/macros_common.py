
from emora_stdm.state_transition_dialogue_manager.macro import Macro
from emora_stdm.state_transition_dialogue_manager.ngrams import Ngrams
from typing import Union, Set, List, Dict, Callable, Tuple, NoReturn, Any
import nltk
try:
    nltk.data.find('wordnet')
except:
    nltk.download('wordnet')

class ONT(Macro):
    def __init__(self, kb):
        self.kb = kb
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.lemmatizer.lemmatize('initialize')
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        node_set = args[0]
        ont_result = self.kb.expressions(self.kb.subtypes(node_set))
        if ngrams:
            lemmas = {self.lemmatizer.lemmatize(gram) for gram in ngrams}
            return lemmas & ont_result
        else:
            return ont_result

class KBQ(Macro):
    def __init__(self, kb):
        self.kb = kb
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.lemmatizer.lemmatize('initialize')
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        kb_result = self.kb.query(*args)
        if ngrams:
            return kb_result & ngrams
        else:
            return kb_result