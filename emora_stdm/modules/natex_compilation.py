
from emora_stdm import NatexNLU, Macro
import spacy

class PartOfSpeech(Macro):
    def __init__(self):
        self.nlp = spacy.load('en_core_web_md')
    def run(self, ngrams, vars, args):
        doc = self.nlp(ngrams.text())
        tokens = list(doc)
        return {token.text for token in tokens if token.pos_.lower() in {x.lower() for x in args}}

vars = {}
natex = NatexNLU('[i, {like, love} $activity=#POS(verb)]', macros={'POS': PartOfSpeech()})

if __name__ == '__main__':
    print('\n', natex, '\n')
    i = input('to match: ')
    print('Match:', bool(natex.match(i, vars=vars, debugging=True)))
    print('\n', 'vars:\n', vars)