
from collections import defaultdict
from emora_stdm.state_transition_dialogue_manager.macro import Macro
from emora_stdm.state_transition_dialogue_manager.ngrams import Ngrams
from emora_stdm.state_transition_dialogue_manager.memory import Memory
from emora_stdm.state_transition_dialogue_manager.utilities import HashableSet, HashableDict, ConfigurationDict
from emora_stdm.state_transition_dialogue_manager.natex_nlg import NatexNLG
from emora_stdm.state_transition_dialogue_manager.natex_nlu import NatexNLU
from emora_stdm.state_transition_dialogue_manager.natex_common import *
from typing import Union, Set, List, Dict, Callable, Tuple, NoReturn, Any
import nltk
from spacy.pipeline import EntityRecognizer
import traceback
import spacy
import sys
try:
    nlp = spacy.load("en_core_web_md")
except Exception as e:
    traceback.print_exc()
    print('Error loading Spacy', file=sys.stderr)
    print('Please run the following command:', file=sys.stderr)
    print('python -m spacy download en_core_web_md', file=sys.stderr)
try:
    nltk.data.find('wordnet')
except:
    nltk.download('wordnet')
try:
    nltk.find('averaged_perceptron_tagger')
except:
    nltk.download('averaged_perceptron_tagger')
from emora_stdm.state_transition_dialogue_manager.wordnet import \
    related_synsets, wordnet_knowledge_base, lemmas_of
from nltk.corpus import wordnet
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
            if (var not in vars and val != 'None') or (var in vars and vars[var] != val):
                return False
        return True


class CheckVarsDisjunction(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        for arg in args:
            var, val = _assignment_to_var_val(arg)
            if (val == 'None' and var not in vars) or (var in vars and vars[var] == val):
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
        configuration = {}
        for arg in args:
            if ':' in arg:
                var, val = arg.split(':')
            elif '=' in arg:
                var, val = arg.split('=')
                if var[0] == '$':
                    var = var[1:]
            else:
                var, val = arg, None
            if val is None:
                if var in vars:
                    configuration[var] = vars[var]
                    configuration[var] = vars[var]
                else:
                    return False
            elif val == 'None':
                if var in vars and vars[var] is not None and vars[var] != 'None':
                    return False
            else:
                if var not in vars or vars[var] != val:
                    return False
        vars['__gate__'] = configuration
        return True


class Unset(Macro):

    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        for var in args:
            if var in vars and vars[var] is not None and vars[var] != 'None':
                return False
        return True


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

class TokLimit(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        if ngrams.text().split() <= int(args[0]):
            return True
        else:
            return False

class Transition(Macro):
    """

    """
    def __init__(self, dialogue_flow):
        self.dialogue_flow = dialogue_flow

    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        if len(args) > 1:
            score = float(args[1])
        else:
            score = 0.5
        target = args[0]
        vars['__converged__'] = 'True'
        self.dialogue_flow.dynamic_transitions().append(
            (NatexNLU('/.*/'),
             (self.dialogue_flow.state(), target, self.dialogue_flow.speaker()),
             score))

class VirtualTransitions(Macro):
    """
    Add transitions from other states to be evaluated. If any of them succeed,
    and their score is higher than other transitions, the target of the imported
    transitions will be the next state.
    """

    def __init__(self, dialogue_flow):
        self.dialogue_flow = dialogue_flow

    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        for state in args:
            if ':' in state:
                controller, state = state.split(':')
                extraction_df = self.dialogue_flow.composite_dialogue_flow().component(controller)
                for source, target, speaker in extraction_df.transitions(state):
                    natex = extraction_df.transition_natex(source, target, speaker)
                    score = extraction_df.transition_settings(source, target, speaker).score
                    if not isinstance(source, tuple):
                        source = (controller, source)
                    if not isinstance(target, tuple):
                        target = (controller, target)
                    self.dialogue_flow.dynamic_transitions().append(
                        (natex, (source, target, speaker), score))
            else:
                for source, target, speaker in self.dialogue_flow.transitions(state):
                    natex = self.dialogue_flow.transition_natex(source, target, speaker)
                    score = self.dialogue_flow.transition_settings(source, target, speaker).score
                    self.dialogue_flow.dynamic_transitions().append(
                        (natex, (source, target, speaker), score))
        return False


class Intent(Macro):

    def _similarity(self, user_utterance, dev_utterance):
        return user_utterance.similarity(dev_utterance)

    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        for i, arg in enumerate(args):
            if isinstance(arg, str) and arg.isnumeric():
                threshold = float(arg)
                del args[i]
                break
        else:
            threshold = 0.0
        user = nlp(ngrams.text())
        dev = [nlp(arg) for arg in args]
        similarity = max([self._similarity(user, x) for x in dev])
        vars['__score__'] = similarity
        if similarity < threshold:
            return False
        else:
            return True


class Default(Macro):

    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        vars['__score__'] = 0.001
        return ''

class CanEnter(Macro):

    def __init__(self, dialogue_flow):
        self.dialogue_flow = dialogue_flow

    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        for state in args:
            if ':' in state:
                component, state = state.split(':')
                enter = self.dialogue_flow.composite_dialogue_flow().\
                    state_settings(component, state).enter
            else:
                enter = self.dialogue_flow.state_settings(state).enter
            if enter is not None and enter.generate() is None:
                return False
        return True


class GoalPursuit(Macro):
    """
    Begin pursuing a goal.

    This sets the current goal to the specified goal, and any outstanding current goal
    will be saved by being pushed onto the goal stack.

    Goals pushed onto the stack are of the form:
    [goal id str, return state str, return phrase str, doom counter int]
    """

    def __init__(self, goal_exit_macro):
        self.goal_exit_macro = goal_exit_macro

    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        if '__stack__' not in vars:
            vars['__stack__'] = []
        if '__goal__' not in vars:
            vars['__goal__'] = 'None'
        if '__goal_return_state__' not in vars:
            vars['__goal_return_state__'] = 'None'
        goal = args[0]
        self.goal_exit_macro.run(ngrams, vars, args)
        vars['__goal__'] = goal


class GoalCompletion(Macro):
    """
    Complete either the current goal, or a specified goal that
    is either the current goal or the first matching on the stack.
    If a goal to complete is specified but not in the stack, this
    macro does nothing.
    """

    def __init__(self, dialogue_flow):
        self.dialogue_flow = dialogue_flow

    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        goal = None
        if len(args) == 1:
            goal = args[0]
        if goal is None or '__goal__' not in vars or goal == vars['__goal__']:
            vars['__goal__'] = 'None'
        else:
            stack = vars['__stack__']
            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == goal:
                    del stack[i]
                    break

class GoalExit(Macro):
    """
    Exit a goal, pushing the current goal onto the stack.
    """

    def __init__(self, dialogue_flow):
        self.dialogue_flow = dialogue_flow
        self.default_return_phrase = ''
        self.default_doom_counter = None

    def goal_return_state(self, goal, vars):
        if '__goal_return_state__' in vars and vars['__goal_return_state__'] != 'None':
            grs = vars['__goal_return_state__']
            vars['__goal_return_state__'] = 'None'
            return grs
        elif goal in self.dialogue_flow.goals() and self.dialogue_flow.goals()[goal]['return_state']:
            return self.dialogue_flow.goals()[goal]['return_state']
        else:
            return vars['__system_state__']

    def goal_return_phrase(self, goal, vars):
        if '__goal_return_phrase__' in vars and vars['__goal_return_phrase__'] != 'None':
            grp = vars['__goal_return_phrase__']
            vars['__goal_return_phrase__'] = 'None'
            return grp
        elif goal in self.dialogue_flow.goals() and self.dialogue_flow.goals()[goal]['return_phrase']:
            return self.dialogue_flow.goals()[goal]['return_phrase']
        else:
            return ''

    def goal_doom_counter(self, goal, vars):
        if '__goal_doom_counter__' in vars and vars['__goal_doom_counter__'] != 'None':
            gdc = vars['__goal_doom_counter__']
            vars['__goal_doom_counter__'] = 'None'
            return gdc
        elif goal in self.dialogue_flow.goals() and self.dialogue_flow.goals()[goal]['doom_counter']:
            return self.dialogue_flow.goals()[goal]['doom_counter']
        else:
            return 'None'

    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        if '__goal__' not in vars:
            vars['__goal__'] = 'None'
        if vars['__goal__'] != 'None':
            push_goal_id = vars['__goal__']
            push_goal_state = self.goal_return_state(push_goal_id, vars)
            push_goal_return_phrase = self.goal_return_phrase(push_goal_id, vars)
            push_goal_doom_counter = self.goal_doom_counter(push_goal_id, vars)
            push_goal = [push_goal_id, push_goal_state, push_goal_return_phrase, push_goal_doom_counter]
            vars['__stack__'].append(push_goal)
        vars['__goal__'] = 'None'


class GoalReturn(Macro):
    """
    Return to the specified goal, or the first goal on the stack.

    Specifying a goal is used for situations where control is taken from a
    goal flow, but the sub-convo actually ends up serving one of the goals
    in the stack. In this case, a transition to the appropriate goal flow
    point can be taken with GoalResume(resumed_goal) called in order to
    return to the goal without any awkward return phrase.

    An optional second argument can be used to return to a specific state.
    An optional third argument can be used for a desired return phrase.
    """

    def __init__(self, dialogue_flow):
        self.dialogue_flow = dialogue_flow

    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        goal = None
        if len(args) > 0 and args[0] != 'None':
            goal = args[0]
        vars['__goal__'] = 'None'
        while vars['__stack__']:
            id, state, phrase, doom = vars['__stack__'].pop()
            if doom != 'None' and doom <= 0:
                continue
            if goal is not None and goal != id:
                continue
            if len(args) > 1 and args[1] != 'None' and args[1] != '':
                state = args[1]
            if len(args) > 2:
                phrase = args[2]
            vars['__target__'] = state
            vars['__goal__'] = id
            return phrase


class SetGoalReturnPoint(Macro):

    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        vars['__goal_return_state__'] = args[0]

class Target(Macro):

    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        if '__target__' not in vars or (vars['__target__'] is None or vars['__target__'] == 'None'):
            vars['__target__'] = args[0]








































