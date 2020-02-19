
from emora_stdm import NatexNLU, NatexNLG, Macro
from emora_stdm.state_transition_dialogue_manager.macros_common import *

class MyMacro(Macro):
    def run(self, ngrams, vars, args):
        result = set()
        # do some processing on ngrams and args
        return result


natex = NatexNLU('[!-{dont, isnt, not} {[I, {like, love, enjoy}, skiing] "I’m into skiing" [skiing {great, my favorite}]}]')

if __name__ == '__main__':

    print(natex.match('i like skiing', debugging=True))
