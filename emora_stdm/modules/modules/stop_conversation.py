from emora_stdm import DialogueFlow, KnowledgeBase, EnumByName
from enum import Enum, auto
import json, os

class State(EnumByName):
    START = auto()
    REC_OFF = auto()
    REC_OFF_2 = auto()
    INSTRUCT_OFF = auto()
    INSTRUCT_OFF_2 = auto()
    REDIRECT = auto()
    END = auto()

TRANSITION_OUT = ["movies", "music", "sports"]

knowledge = KnowledgeBase()
knowledge.load_json_file(os.path.join('modules',"stop_convo.json"))
df = DialogueFlow(State.START, initial_speaker=DialogueFlow.Speaker.USER, kb=knowledge)
df.add_state(State.START)#, error_successor=State.START)
df.add_state(State.INSTRUCT_OFF, error_successor=State.REDIRECT)
df.add_state(State.INSTRUCT_OFF_2, error_successor=State.REDIRECT)
df.add_system_transition(State.START, State.START, "NULL TRANSITION")

stop_nlu = [
    "[$off_phrase=[!#ONT(ontturn), #ONT(ontoff)]]",
    "[$off_phrase=[!#ONT(ontturn), to, #ONT(ontoff)]]",
    "$off_phrase=[!{alexa,echo,computer}?, #ONT(ontoff)]",
    "[$off_phrase=[!{alexa,echo,computer,#ONT(ontturn)}, #ONT(ontoffpaired)]]",
    "[$off_phrase=[!{alexa,echo,computer,#ONT(ontturn)}, to, #ONT(ontoffpaired)]]",
    "[$off_phrase={goodnight, good night,shut up}]"
]

#df.add_user_transition(State.START, State.REC_OFF, stop_nlu)

instr_nlg = ['[! I heard you say $off_phrase,"." If you would like to exit the conversation"," say Alexa stop"."]']
df.add_system_transition(State.REC_OFF, State.INSTRUCT_OFF, instr_nlg)

df.add_user_transition(State.INSTRUCT_OFF, State.REC_OFF_2, stop_nlu)

instr_nlg_strong = ['[! I am sorry"," but I have a hard time understanding phrases like $off_phrase because '
                    'it seems like you want to stop talking to me"." If you actually do want to stop talking right now"," '
                    'you must say Alexa stop"." Otherwise"," I am happy to keep talking"," especially about '
                    + ' or '.join(TRANSITION_OUT) + "]"]
df.add_system_transition(State.REC_OFF_2, State.INSTRUCT_OFF_2, instr_nlg_strong)

redirect_nlg = ['[! Ok then"," I seem to have gotten my signals crossed"."]',
                '[! Ok"," let us pick up the conversation again"."]',
                '[! I see"," let us get back to talking then"."]',
                ]
df.add_system_transition(State.REDIRECT, State.END, redirect_nlg)
df.update_state_settings(State.END, system_multi_hop=True)


if __name__ == '__main__':
    # automatic verification of the DialogueFlow's structure (dumps warnings to stdout)
    df.check()
    # run the DialogueFlow in interactive mode to test
    df.run(debugging=True)