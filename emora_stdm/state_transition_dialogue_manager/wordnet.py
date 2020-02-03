
import nltk
try:
    nltk.data.find('wordnet')
except:
    nltk.download('wordnet')

from nltk.corpus import wordnet as wn


def synonyms(word):
    l = set()
    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            l.add(lemma.name().replace('_', ' '))
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
        l.update({x.name().replace('_', ' ') for x in syn.lemmas()})
        hypo_syns = _hyponyms(syn)
        for hypo_syn in hypo_syns:
            l.update({x.name().replace('_', ' ') for x in hypo_syn.lemmas()})
    return l


