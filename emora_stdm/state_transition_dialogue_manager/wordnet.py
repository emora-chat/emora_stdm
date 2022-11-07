import sys
from time import time
import nltk
try:
    nltk.data.find('corpora/wordnet.zip')
except LookupError:
    nltk.download('wordnet')

from nltk.corpus import wordnet as wn
import os
from emora_stdm.state_transition_dialogue_manager.knowledge_base import KnowledgeBase

wordnet_knowledge_base = KnowledgeBase()

import importlib_resources as impr
from . import data
try:
    pass
    # t1 = time()
    # sys.stderr.write('Loading wordnet.json... ')
    # json_str = impr.read_text(data, 'wordnet.json')
    # wordnet_knowledge_base.load_json_string(json_str)
    # sys.stderr.write(' done in {}s'.format(time() - t1))
except FileNotFoundError:
    sys.stderr.write(' failed to load.')

def related_synsets(word):
    """
    returns lemmas
    """
    related = set()
    synsets = wn.synsets(word)
    for lemma in set().union(*[set(x.lemmas()) for x in synsets]):
        derivations = lemma.derivationally_related_forms()
        related.add(lemma.synset())
        for derivation in derivations:
            related.add(derivation.synset())
    return related

def lemmas_of(synset):
    return {x.name().replace('_', ' ').lower() for x in synset.lemmas()}

def synonyms(word):
    l = set()
    for syn in wn.synsets(word):
        l.update(lemmas_of(syn))
    return l

def _hyponyms(synset):
    hypos = synset.hyponyms()
    if hypos:
        result = hypos
        for hypo in list(hypos):
            result.extend(_hyponyms(hypo))
        return result
    else:
        return hypos

def hyponyms(word):
    l = set()
    for syn in wn.synsets(word):
        l.update(lemmas_of(syn))
        hypo_syns = _hyponyms(syn)
        for hypo_syn in hypo_syns:
            l.update(lemmas_of(hypo_syn))
    return l
