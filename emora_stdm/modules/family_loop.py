
from emora_stdm import DialogueFlow, NatexNLU, NatexNLG, Macro


df = DialogueFlow(initial_state="root", kb='family.json')


root = 'root'
df.add_state(root, error_successor=root)
df.add_system_transition(root, root, '{yeah, for sure, okay}', score=0)



## related person
df.var_dependencies()['related_type'] = {'related_personality'}

# S: Who do you live with?
root = 'root'
df.add_state('opening live with', system_multi_hop=True)
df.add_system_transition('opening live with', root, '')
df.add_system_transition(root, 'opening live with',
'[!#GATE() "So, who do you live with?"]', score=0.001)

# S: Who are you close to?
root = 'root'
df.add_state('opening close to', system_multi_hop=True)
df.add_system_transition('opening close to', root, '')
df.add_system_transition(root, 'opening close to',
'[!#GATE() "So tell me, who are you closest to in your life?"]', score=0.001)

# U: my $related_type
root = 'root'
df.add_state('related', root, user_multi_hop=True)
df.add_user_transition(root, 'related',
                       '[my $related_type=#ONTE(related_person)]', score=0.5)

df.add_state('related and personality', root, user_multi_hop=True)
df.add_user_transition(root, 'related and personality',
'[my $related_type=#ONTE(related_person) #NOT(#EXP(negation)) $related_personality=#ONTE(personality_trait)]')

# S: What is $related_type like?
root = 'root'
df.add_state('ask related personality', error_successor=root)
df.add_system_transition(root, 'ask related personality',
                         '[!#GATE(related_type, related_personality:None) "Oh, what is your" $related_type "like?"]')
df.add_state('respond related personality', error_successor=root, user_multi_hop=True)
df.add_user_transition('ask related personality', 'respond related personality',
                       '[[!#NOT(#EXP(negation)) $related_personality=#ONTE(personality_trait)]]')

# Comment on $related_personality
root = 'root'
df.add_state('comment related personality', system_multi_hop=True)
df.add_system_transition('comment related personality', root, '')
df.add_system_transition(root, 'comment related personality',
'[!#GATE(related_type, related_personality) so #FPP($related_type) is $related_personality]')

# S: Do you get along with your $related_type?
root = 'root'
df.add_state('ask get along', error_successor=root)
df.add_system_transition(root, 'ask get along',
'[!#GATE(related_type, related_get_along:None) "Do you get along with your" $related_type "?"]')

# S: What is new with your $related_type?
root = 'root'
df.add_state('ask related new', error_successor=root)
df.add_system_transition(root, 'ask related new',
'[!#GATE(related_type, related_new_event:None) "So what is new with your" $related_type "?"]')



# Ask $related_type occupation

if __name__ == '__main__':
    df.run(debugging=True)
