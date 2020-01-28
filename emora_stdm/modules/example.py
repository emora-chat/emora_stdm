
from emora_stdm import DialogueFlow
from enum import Enum

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

if __name__ == '__main__':
    df.check()
    df.run(debugging=True)

