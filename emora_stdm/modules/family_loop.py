
from emora_stdm import DialogueFlow, NatexNLU, NatexNLG, Macro


df = DialogueFlow(initial_state="start", kb='family.json')

df.add_state('root')

df.add_state('living with prompt')
df.add_state('living with reaction')
df.add_state('personality')
df.add_state('personality reaction')

