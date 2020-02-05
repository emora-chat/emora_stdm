from enum import Enum,auto
from emora_stdm import DialogueFlow
import json

yes_nlu = '[[! -{not,dont} {#EXP(yes),#ONT(yes_qualifier),#EXP(like)}]]'
df.add_user_transition(State.PROMPT_HOBBY, State.LIKE_HOBBY, yes_nlu)
