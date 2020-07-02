
from emora_stdm import Macro

class Repeated(Macro):
    def run(self, ngrams, vars, args):
        word_to_repeat = args[0]
        number_of_repetitions = int(args[1])
        return ' '.join([word_to_repeat] * number_of_repetitions)

from emora_stdm import NatexNLU

if __name__ == '__main__':
    natex = NatexNLU('oh hello #Rep(there, 3) how are you', macros={'Rep': Repeated()})
    assert natex.match('oh hello there there there how are you', debugging=True)