from enum import Enum,auto
from emora_stdm import DialogueFlow
import json

class State(Enum):
    PRESTART = auto()
    FIRST_ASK_HOBBY = auto()
    GEN_ASK_HOBBY = auto()
    REC_HOBBY = auto()
    RECOG_NO_INFO_HOBBY = auto()
    ASK_FAVE_THING = auto()
    EXPERIENCE = auto()
    CHALLENGE = auto()
    UNSURE = auto()
    NO_RECOG_FAVE = auto()
    NO_RECOG_HOBBY = auto()
    PROMPT_HOBBY = auto()
    READING_GENRE = auto()
    LIKE_READING = auto()
    ACK_NO_LIKE = auto()
    ACK_NEVER_TRIED = auto()
    PROMPT_RES_ERR = auto()
    LIKE_HOBBY = auto()
    LIKE_HOBBY_ERR = auto()
    ASK_GENRE = auto()
    UNRECOG_GENRE = auto()
    ACK_END = auto()
    END = auto()

PUBLIC_ENUMS = {
        'Speaker': DialogueFlow.Speaker,
        'State': State
    }

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) in PUBLIC_ENUMS.values():
            return {"__enum__": str(obj)}
        return json.JSONEncoder.default(self, obj)


def as_enum(d):
    if "__enum__" in d:
        name, member = d["__enum__"].split(".")
        return getattr(PUBLIC_ENUMS[name], member)
    else:
        return d

mem = []
t = (State.GEN_ASK_HOBBY, State.REC_HOBBY, DialogueFlow.Speaker.SYSTEM)
mem.append(t)
en_mem = json.dumps(mem, cls=EnumEncoder)
de_mem = json.loads(en_mem, object_hook=as_enum)
print(tuple(de_mem[0]) in mem)
print(t in mem)
print()
