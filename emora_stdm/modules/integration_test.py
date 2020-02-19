
from emora_stdm.modules.modules.family_loop import df

import json
from emora_stdm import HashableDict
from emora_stdm import DialogueFlow

from emora_stdm.state_transition_dialogue_manager.composite_dialogue_flow import CompositeDialogueFlow

cdf = CompositeDialogueFlow('start', initial_speaker=DialogueFlow.Speaker.SYSTEM)
cdf.add_component(df, 'family')
cdf.add_system_transition('start', ('family', 'root'), 'hello')

from collections import defaultdict
PUBLIC_ENUMS = {
    'Speaker': DialogueFlow.Speaker
}
class SpecializedEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) in PUBLIC_ENUMS.values():
            return {"__enum__": str(obj)}
        elif isinstance(obj, set):
            return {"__set__": list(obj)}
        return json.JSONEncoder.default(self, obj)
def as_specialized(d):
    if "__enum__" in d:
        name, member = d["__enum__"].split(".")
        return getattr(PUBLIC_ENUMS[name], member)
    elif "__set__" in d:
        return set([HashableDict(x) for x in d["__set__"]])
    else:
        return d
def encode_state(item):
    if isinstance(item, tuple):
        if item[0] != "SYSTEM":
            item = item[0] + "|" + item[1]
        else:
            item = item[1]
    return item
def decode_state(item):
    item = item.split("|")
    if len(item) > 1:
        return item[0], item[1]
    return item[0]

if __name__ == '__main__':

    while True:
        text = input("U: ")
        cdf.user_turn(text, debugging=True)
        intermediate_state = cdf.state()
        response = cdf.system_turn(debugging=True)
        final_state = cdf.state()
        print("State after sys trans: %s" % str(final_state))
        print()
        print("NORMAL GATES (controller): ")
        print(cdf.controller().gates())
        print()
        # GATE SERIALIZATION
        json_gates = {}
        for name, component in cdf._components.items():
            json_gates[name] = {}
            for trans,hash_dicts in component.gates().items():
                new_tup = encode_state(trans[0]) + "||" + encode_state(trans[1]) + "||" + str(trans[2])
                json_gates[name][new_tup] = hash_dicts
        json_gates = json.dumps(json_gates, cls=SpecializedEncoder)
        print()
        print("SERIALIZED GATES (controller): ")
        print(json_gates)
        print()
        # GATE DESERIALIZATION
        if json_gates is not None:
            saved_gates = json.loads(json_gates, object_hook=as_specialized)
            for name, gates in saved_gates.items():
                component = cdf.component(name)
                new_gates = defaultdict(set)
                for encoded_trans, dict_set in gates.items():
                    trans_split = encoded_trans.split("||")
                    enum, member = trans_split[2].split(".")
                    speaker = getattr(PUBLIC_ENUMS[enum], member)
                    new_gates[(decode_state(trans_split[0]), decode_state(trans_split[1]), speaker)] = dict_set
                component._gates = new_gates
        print()
        print("DESERIALIZED GATES (controller): ")
        print(cdf.controller().gates())
        print()
        print("S: %s"%response)