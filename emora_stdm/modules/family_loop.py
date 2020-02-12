
from emora_stdm import DialogueFlow, NatexNLU, NatexNLG, Macro


df = DialogueFlow(initial_state="root", kb='family.json')

df.add_state('root', error_successor='root')
df.add_system_transition('root', 'root', '{yeah, for sure, okay}', score=0)

################### USER LOOPS ####################

# Mention related person
# capture related_type
df.add_state('related', 'root', user_multi_hop=True)
df.add_user_transition('root', 'related',
                       '[my $related_type=#ONTE(related_person)]')

################### SYSTEM LOOPS ####################

# Ask what $related_type is like
df.add_state('ask related personality', error_successor='root')
df.add_system_transition('root', 'ask related personality', '[!"Oh, what is your" $related_type "like?"]')
df.add_state('respond related personality', error_successor='root', user_multi_hop=True)
df.add_user_transition('ask related personality', 'respond related personality',
                       '[$related_personality=[!#NOT(#EXP(negation)) #ONTE(personality)]]')

if __name__ == '__main__':
    df.run(debugging=True)
