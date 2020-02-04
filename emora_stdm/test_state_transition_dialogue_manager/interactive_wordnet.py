
from emora_stdm.state_transition_dialogue_manager.macros_common import WN
from emora_stdm.state_transition_dialogue_manager.ngrams import Ngrams


wn = WN()

if __name__ == '__main__':

    while True:
        i = input('Enter "<WN ARG>", or "<PHRASE> in <WN ARG>": ')
        if ' in ' in i:
            i = [x.strip() for x in i.split(' in ')]
            print(i[0] in wn.run(Ngrams(i[0]), {}, [i[1]]))
        else:
            print(wn.run(None, {}, [i]))

