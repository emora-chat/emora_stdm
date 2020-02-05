
from collections import defaultdict
from emora_stdm.state_transition_dialogue_manager.macro import Macro
from emora_stdm.state_transition_dialogue_manager.ngrams import Ngrams
from typing import Union, Set, List, Dict, Callable, Tuple, NoReturn, Any
import nltk
try:
    nltk.data.find('wordnet')
except:
    nltk.download('wordnet')
from nltk.corpus import wordnet
from emora_stdm.state_transition_dialogue_manager.wordnet import \
    related_synsets, wordnet_knowledge_base, lemmas_of
import regex

class ONTE(Macro):
    """
    get the set of expressions matching the entire descendent subtree
    underneath a given set of ontology nodes (usually 1)
    """
    def __init__(self, kb):
        self.kb = kb
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.lemmatizer.lemmatize('initialize')
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        if isinstance(args, list):
            node_set = set(args)
        elif isinstance(args, str):
            node_set = {args}
        elif isinstance(args, set):
            node_set = args
        else:
            raise Exception("Args to ONTE were of wrong format: must be list, str, or set")
        ont_result = self.kb.expressions(self.kb.subtypes(node_set))
        if ngrams:
            lemma_map = defaultdict(set)
            for gram in ngrams:
                for pos in 'a', 'r', 'v', 'n':
                    lemma = self.lemmatizer.lemmatize(gram, pos=pos)
                    lemma_map[lemma].add(gram)
            matches = lemma_map.keys() & ont_result
            return set().union(*[lemma_map[match] for match in matches])
        else:
            return ont_result

class ONTN(Macro):
    """
    get the set of node names matching the entire descendent subtree
    underneath a given set of ontology nodes (usually 1)
    """
    def __init__(self, kb):
        self.kb = kb
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.lemmatizer.lemmatize('initialize')
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        if isinstance(args, list):
            node_set = set(args)
        elif isinstance(args, str):
            node_set = {args}
        elif isinstance(args, set):
            node_set = args
        else:
            raise Exception("Args to ONTE were of wrong format: must be list, str, or set")
        ont_result = self.kb.subtypes(node_set) - node_set
        if ngrams:
            lemma_map = defaultdict(set)
            for gram in ngrams:
                for pos in 'a', 'r', 'v', 'n':
                    lemma = self.lemmatizer.lemmatize(gram, pos=pos)
                    lemma_map[lemma].add(gram)
            matches = lemma_map.keys() & ont_result
            return set().union(*[lemma_map[match] for match in matches])
        else:
            return ont_result


class ONT_NEG(Macro):
    def __init__(self, kb):
        self.kb = kb
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.lemmatizer.lemmatize('initialize')

    def run(self, ngrams, vars, args):
        node_set = args[0]
        ont_result = self.kb.expressions(self.kb.subtypes(node_set))
        if len(ont_result.intersection(ngrams)) > 0:
            return False
        return True

class NOT(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        processedargs = set()
        for arg in args:
            if isinstance(arg, list):
                processedargs.update(set(arg))
            elif isinstance(arg, str):
                processedargs.add(str(arg))
            elif isinstance(arg, set):
                processedargs.update(arg)
            else:
                raise Exception("Args to WN were of wrong format: must be list, str, or set")
        if processedargs & ngrams:
            return False
        else:
            return True

class KBE(Macro):
    """
    get the set of expressions matching the nodes returned from a KB
    query, where the first arg is a set of starting nodes (or single node)
    and each following arg is a (set or single) relation to traverse
    """
    def __init__(self, kb):
        self.kb = kb
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.lemmatizer.lemmatize('initialize')
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        kb_result = self.kb.expressions(self.kb.query(*args))
        if ngrams:
            lemma_map = defaultdict(set)
            for gram in ngrams:
                for pos in 'a', 'r', 'v', 'n':
                    lemma = self.lemmatizer.lemmatize(gram, pos=pos)
                    lemma_map[lemma].add(gram)
            matches = lemma_map.keys() & kb_result
            return set().union(*[lemma_map[match] for match in matches])
        else:
            return kb_result

class EXP(Macro):
    def __init__(self, kb):
        self.kb = kb
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.lemmatizer.lemmatize('initialize')
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        kb_result = self.kb.expressions(*args)
        if ngrams:
            lemma_map = defaultdict(set)
            for gram in ngrams:
                for pos in 'a', 'r', 'v', 'n':
                    lemma = self.lemmatizer.lemmatize(gram, pos=pos)
                    lemma_map[lemma].add(gram)
            matches = lemma_map.keys() & kb_result
            return set().union(*[lemma_map[match] for match in matches])
        else:
            return kb_result

class WN(Macro):
    def __init__(self, kb=None):
        if kb is None:
            kb = wordnet_knowledge_base
        self.kb = kb
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.lemmatizer.lemmatize('initialize')

    def run(self, ngrams: Union[Ngrams, None], vars: Dict[str, Any], args: List[Any]):
        if isinstance(args, list):
            node_set = set(args)
        elif isinstance(args, str):
            node_set = {args}
        elif isinstance(args, set):
            node_set = args
        else:
            raise Exception("Args to WN were of wrong format: must be list, str, or set")
        expanded_set = set()
        for word in node_set:
            expanded_set.update({x.name() for x in related_synsets(word)})
        subtypes = self.kb.subtypes(expanded_set)
        ont_result = set(self.kb.expressions(subtypes))
        second_order = set()
        for subtype in subtypes:
            synset = wordnet.synset(subtype)
            for lemma in synset.lemmas():
                dlemmas = lemma.derivationally_related_forms()
                second_order.update({dlemma.synset().name() for dlemma in dlemmas})
                ont_result.update({dlemma.name().replace('_', ' ').lower() for dlemma in dlemmas})
        second_order.difference_update(subtypes)
        ont_result.update(self.kb.expressions(self.kb.subtypes(second_order)))
        if ngrams:
            lemma_map = defaultdict(set)
            for gram in ngrams:
                for pos in 'a', 'r', 'v', 'n':
                    lemma = self.lemmatizer.lemmatize(gram, pos=pos)
                    lemma_map[lemma].add(gram)
            matches = lemma_map.keys() & ont_result
            return set().union(*[lemma_map[match] for match in matches])
        else:
            return ont_result


class UnionMacro(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        sets = []
        for arg in args:
            if isinstance(arg, set):
                sets.append(arg)
            if isinstance(arg, str):
                sets.append({arg})
            elif isinstance(arg, list):
                sets.append(set(arg))
        return set().union(*sets)

class Intersection(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        sets = []
        for arg in args:
            if isinstance(arg, set):
                sets.append(arg)
            if isinstance(arg, str):
                sets.append({arg})
            elif isinstance(arg, list):
                sets.append(set(arg))
        if sets:
            return set.intersection(*sets)
        else:
            return set()

class Difference(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        if len(args) != 2:
            raise ValueError('DIFF macro expects 2 args')
        sets = []
        for arg in args:
            if isinstance(arg, set):
                sets.append(arg)
            if isinstance(arg, str):
                sets.append({arg})
            elif isinstance(arg, list):
                sets.append(set(arg))
        return sets[0] - sets[1]

def _assignment_to_var_val(arg):
    var = arg[arg.find('<') + 1:arg.find('>')]
    val = arg[arg.find('>') + 1:-1]
    return var, val

class SetVars(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        for arg in args:
            var, val = _assignment_to_var_val(arg)
            vars[var] = val
        return None

class CheckVarsConjunction(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        for arg in args:
            var, val = _assignment_to_var_val(arg)
            if var not in vars or vars[var] != val:
                return False
        return True


class CheckVarsDisjunction(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        for arg in args:
            var, val = _assignment_to_var_val(arg)
            if var in vars and vars[var] == val:
                return True
        return False