
import nltk
try:
    nltk.data.find('wordnet')
except:
    nltk.download('wordnet')

from nltk.corpus import wordnet as wn
import os
from emora_stdm.state_transition_dialogue_manager.knowledge_base import KnowledgeBase


wordnet_knowledge_base = KnowledgeBase()

try:
    wordnet_knowledge_base.load_json_file('data/wordnet.json')
except FileNotFoundError:
    print('Could not find wordnet.json')

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
