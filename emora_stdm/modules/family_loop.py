
from emora_stdm import DialogueFlow, NatexNLU, NatexNLG, Macro


df = DialogueFlow(initial_state="root", kb='family.json')

df.add_state('root', error_successor='root')
df.add_system_transition('root', 'root', '{yeah, for sure, okay}', score=0)

################### USER LOOPS ####################

# Mention related person
# capture related_type
df.add_state('related', 'root', user_multi_hop=True)
df.add_user_transition('root', 'related',
                       '[my $focus=$related_type=#ONTE(related_person)]', score=0.5)

################### SYSTEM LOOPS ####################


## related person
df.var_dependencies()['related_type'] = {'related_personality'}

# Ask what $related_type is like
df.add_state('ask related personality', error_successor='root')
df.add_system_transition('root', 'ask related personality',
                         '[!#GATE($related_type) "Oh, what is your" $related_type "like?"]')
df.add_state('respond related personality', error_successor='root', user_multi_hop=True)
df.add_user_transition('ask related personality', 'respond related personality',
                       '[[!#NOT(#EXP(negation)) $related_personality=#ONTE(personality_trait)]]')

# Comment on $related_personality
df.add_state('comment related personality', system_multi_hop=True)
df.add_system_transition('comment related personality', 'root', '')
df.add_system_transition('root', 'comment related personality',
'[!#GATE($related_type, $related_personality) so #FPP($related_type) is $related_personality]')

# Ask $related_type occupation


if __name__ == '__main__':
    df.run(debugging=True)
