
from collections import defaultdict
from emora_stdm.state_transition_dialogue_manager.macro import Macro
from emora_stdm.state_transition_dialogue_manager.ngrams import Ngrams
from emora_stdm.state_transition_dialogue_manager.memory import Memory
from emora_stdm.state_transition_dialogue_manager.utilities import HashableSet, HashableDict, ConfigurationDict
from emora_stdm.state_transition_dialogue_manager.natex_nlg import NatexNLG
from emora_stdm.state_transition_dialogue_manager.natex_nlu import NatexNLU
from typing import Union, Set, List, Dict, Callable, Tuple, NoReturn, Any
import nltk
from spacy.pipeline import EntityRecognizer
import traceback
import spacy
import sys
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    traceback.print_exc()
    print('Error loading Spacy', file=sys.stderr)
    print('Please run the following command:', file=sys.stderr)
    print('python -m spacy download en_core_web_sm', file=sys.stderr)
try:
    nltk.data.find('wordnet')
except:
    nltk.download('wordnet')
try:
    nltk.find('averaged_perceptron_tagger')
except:
    nltk.download('averaged_perceptron_tagger')
from nltk.corpus import wordnet
from emora_stdm.state_transition_dialogue_manager.wordnet import \
    related_synsets, wordnet_knowledge_base, lemmas_of
import regex


def _process_args_set(args, vars):
    for i, e in enumerate(args):
        if isinstance(e, str) and '$' == e[0]:
            args[i] = vars[e[1:]]
    return args

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
        node_set = set(_process_args_set(args, vars))
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
        node_set = set(_process_args_set(args, vars))
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
                if arg[0] == '$':
                    arg = vars[arg[1:]]
                processedargs.add(str(arg))
            elif isinstance(arg, set):
                processedargs.update(arg)
            elif isinstance(arg, bool):
                return not bool
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
        args = _process_args_set(args, vars)
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
        args = _process_args_set(args, vars)
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
        node_set = set(_process_args_set(args, vars))
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
                if arg[0] == '$':
                    arg = vars[arg[1:]]
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
                if arg[0] == '$':
                    arg = vars[arg[1:]]
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
                if arg[0] == '$':
                    arg = vars[arg[1:]]
                sets.append({arg})
            elif isinstance(arg, list):
                sets.append(set(arg))
        return sets[0] - sets[1]

def _assignment_to_var_val(arg):
    match = regex.match(r'\$([^=]+)=(.*)', arg)
    var, val = match.groups()
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

class IsPlural(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        arg = args[0]
        if isinstance(arg, str) and arg[0] == '$':
            arg = vars[arg[1:]]
        pos = nltk.pos_tag(arg.split())[-1][1]
        if pos == 'NNS':
            return True
        return False

class FirstPersonPronoun(Macro):
    def __init__(self, kb):
        self.kb = kb
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        args = _process_args_set(args, vars)
        if IsPlural()(None, None, [args[0]]):
            return 'they'
        elif args[0] in ONTE(self.kb)({args[0]}, None, ['female']):
            return 'she'
        elif args[0] in ONTE(self.kb)({args[0]}, None, ['male']):
            return 'he'
        elif args[0] not in ONTE(self.kb)({args[0]}, None, ['person']):
            return 'it'
        else:
            return 'they'

class ThirdPersonPronoun(Macro):
    def __init__(self, kb):
        self.kb = kb
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        args = _process_args_set(args, vars)
        if IsPlural()(None, None, [args[0]]):
            return 'them'
        elif args[0] in ONTE(self.kb)({args[0]}, None, ['female']):
            return 'her'
        elif args[0] in ONTE(self.kb)({args[0]}, None, ['male']):
            return 'him'
        elif args[0] not in ONTE(self.kb)({args[0]}, None, ['person']):
            return 'it'
        else:
            return 'them'

class PossessivePronoun(Macro):
    def __init__(self, kb):
        self.kb = kb
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        args = _process_args_set(args, vars)
        if IsPlural()(None, None, [args[0]]):
            return 'their'
        elif args[0] in ONTE(self.kb)({args[0]}, None, ['female']):
            return 'her'
        elif args[0] in ONTE(self.kb)({args[0]}, None, ['male']):
            return 'his'
        elif args[0] not in ONTE(self.kb)({args[0]}, None, ['person']):
            return 'its'
        else:
            return 'their'

class Equal(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        args = _process_args_set(args, vars)
        for i in range(len(args)-1):
            if args[i] != args[i+1]:
                return False
        return True

class Gate(Macro):
    def __init__(self, dialogue_flow):
        self.dialogue_flow = dialogue_flow
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        configuration = ConfigurationDict()
        requirements = {}
        for arg in args:
            if isinstance(arg, str) and ':' in arg:
                var, val = arg.split(':')
                var = var.strip()
                val = val.strip()
                if val == 'None':
                    val = None
                requirements[var] = val
                if var in vars:
                    configuration[var] = vars[var]
                else:
                    configuration[var] = None
            else:
                if arg in vars:
                    configuration[arg] = vars[arg]
                else:
                    configuration[arg] = None
        self.dialogue_flow.set_gate_requirements(requirements)
        if self.dialogue_flow.passes_gate(configuration):
            self.dialogue_flow.buffer_configuration(configuration)
            return True
        else:
            return False


class Clear(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        for arg in args:
            if arg in vars:
                vars[arg] = None


class NamedEntity(Macro):
    """
    NER tags: PERSON, NORP, FAC, ORG, GPE, LOC, PRODUCT, EVENT, WORK_OF_ART, LAW, LANGUAGE,
              DATE, TIME, PERCENT, MONEY, QUANTITY, ORDINAL, CARDINAL
        https://spacy.io/api/annotation
    """
    def __init__(self):
        pass
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        doc = nlp(ngrams.text())
        entities = set()
        for ent in doc.ents:
            if not args or ent.label_.lower() in {x.lower() for x in args}:
                entities.add(ent.text)
        return entities

class PartOfSpeech(Macro):
    def __init__(self):
        pass
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        doc = nlp(ngrams.text())
        return {token.text for token in doc if token.pos_.lower() in {x.lower() for x in args}}

class Lemma(Macro):
    """
    get the set of expressions matching the entire descendent subtree
    underneath a given set of ontology nodes (usually 1)
    """
    def __init__(self):
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.lemmatizer.lemmatize('initialize')
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        if ngrams:
            lemma_map = defaultdict(set)
            for gram in ngrams:
                for pos in 'a', 'r', 'v', 'n':
                    lemma = self.lemmatizer.lemmatize(gram, pos=pos)
                    lemma_map[lemma].add(gram)
            matches = lemma_map.keys() & args
            return set().union(*[lemma_map[match] for match in matches])

class Score(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        score = None
        for arg in args:
            if '=' in arg:
                var, val = _assignment_to_var_val(arg)
                if var not in vars or vars[var] != val:
                    return
            else:
                score = float(arg)
        vars['__score__'] = score