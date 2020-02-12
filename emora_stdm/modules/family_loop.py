
from emora_stdm import DialogueFlow, NatexNLU, NatexNLG, Macro


df = DialogueFlow(initial_state="root", kb='family.json')

df.add_state('root', error_successor='root')
df.add_system_transition('root', 'root', '{yeah, for sure, okay}', score=0)

# related
df.add_state('related', 'root', user_multi_hop=True)
df.add_user_transition('root', 'related',
                       [
                           '[!my $related_type=#ONTE(partner)]',
                           '[!my $related_type=#ONTE(parent)]'
                       ])

if __name__ == '__main__':
    df.run(debugging=True)
