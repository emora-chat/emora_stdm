from emora_stdm import NatexNLU, NatexNLG, DialogueFlow
from enum import Enum


# do you have any pets
# i have a cat
# do you like your cat
# yes
# thats great

# do you have any pets
# i have a dog
# do you like your dog
# no
# im sorry

class States(Enum):
    START = 0
    ASK_PET = 1
    HEAR_PET = 2
    ASK_LIKE = 3
    HEAR_YES = 4
    HEAR_NO = 5
    ACK_YES = 6
    ACK_NO = 7
    ERR = 8



df = DialogueFlow(States.START, initial_speaker=DialogueFlow.Speaker.SYSTEM)

df.add_system_transition(States.START, States.ASK_PET)