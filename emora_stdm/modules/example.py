
from emora_stdm import DialogueFlow
from enum import Enum

from emora_stdm import NatexNLU

class State(Enum):
    START = 0
    FAM_ANS = 1
    FAM_Y = 2
    FAM_N = 3
    FAM_ERR = 4
    WHATEV = 5

df = DialogueFlow(State.START)

df.add_system_transition(State.START, State.FAM_ANS, '[!do you have a $F={brother, sister, son, daughter, cousin}]')
df.add_user_transition(State.FAM_ANS, State.FAM_Y, '[{yes, yea, yup, yep, i do, yeah}]')
df.add_user_transition(State.FAM_ANS, State.FAM_N, '[{no, nope}]')
df.add_system_transition(State.FAM_Y, State.WHATEV, 'thats great i wish i had a $F')
df.add_system_transition(State.FAM_N, State.WHATEV, 'ok then')
df.add_system_transition(State.FAM_ERR, State.WHATEV, 'im not sure i understand')

df.set_error_successor(State.FAM_ANS, State.FAM_ERR)
df.set_error_successor(State.WHATEV, State.START)


user_not_have_dog = NatexNLU('[dont, dog]')
user_has_dog_or_cat = NatexNLU('[![{cat, dog}] #NOT(dont)]')

if __name__ == '__main__':

    #match = user_not_have_dog.match('i dont have a dog', debugging=True)
    #print('Match:', match)

    match = user_has_dog_or_cat.match('i have dont cat', debugging=True)

    print('Match:', match)

    #df.check()
    #df.run(debugging=True)

