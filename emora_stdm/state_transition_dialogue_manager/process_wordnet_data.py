import os
import nltk
try:
    nltk.data.find('wordnet')
except:
    nltk.download('wordnet')

from nltk.corpus import wordnet as wn
import emora_stdm.state_transition_dialogue_manager.wordnet as stdmwn
from emora_stdm.state_transition_dialogue_manager.knowledge_base import KnowledgeBase
from structpy.collection import Multibidict


if __name__ == '__main__':

    if not os.path.isdir('data'):
        os.mkdir('data')
    if not os.path.isfile('data/count_1w.txt'):
        os.system('wget -O data/count_1w.txt https://norvig.com/ngrams/count_1w.txt')
    if not os.path.isfile('data/count_2w.txt'):
        os.system('wget -O data/count_2w.txt https://norvig.com/ngrams/count_2w.txt')


    def process_counts(file, count_cutoff=None):
        d = {}
        for line in file:
            line = line.split()
            gram = ' '.join(line[:-1])
            count = int(line[-1])
            if not count_cutoff or count > count_cutoff:
                d[gram] = count
        return d

    counts1w = open('data/count_1w.txt')
    counts2w = open('data/count_2w.txt')

    counts_dict = {**process_counts(counts1w, 100000), **process_counts(counts2w, 100000)}

    # (subtype, type)
    type_arcs = set()
    expr_arcs = set()


    i = 0
    for synset in wn.all_synsets():
        hyponyms = synset.hyponyms()
        for hyponym in hyponyms:
            sub_hyponyms = hyponym.hyponyms()
            if not sub_hyponyms:
                lemmas = {x.name().replace('_', ' ') for x in hyponym.lemmas()}
                for lemma in list(lemmas):
                    if lemma not in counts_dict or counts_dict[lemma] < 0:
                        lemmas.remove(lemma)
                if lemmas:
                    type_arcs.add((hyponym.name(), synset.name()))
                for lemma in lemmas:
                    expr_arcs.add((hyponym.name(), lemma))
            else:
                type_arcs.add((hyponym.name(), synset.name()))
                for lemma in hyponym.lemmas():
                    expr_arcs.add((hyponym.name(), lemma.name().replace('_', ' ')))
        i += 1
        if i % 1000 == 0:
            print(i, 'processed')

    print('done')
    print(len(type_arcs))

    kb = KnowledgeBase(arcs={(x, 'type', y) for x, y in type_arcs}
                             | {(x, 'expr', y) for x, y in expr_arcs})

    output = open('data/wordnet.json', 'w')
    output.write(kb.to_json())

'''
    while True:
        i = input('>> ')
        try:
            synsets = wn.synsets(i)
            result = set()
            for synset in synsets:
                result.update(kb.expressions(kb.subtypes(synset.name())))
            print(result)
        except:
            print('nope')
'''