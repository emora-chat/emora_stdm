
from emora_stdm import DialogueFlow, NatexNLU, NatexNLG, Macro


df = DialogueFlow(initial_state="start", kb='family.json')

# living with
df.add_state('living with prompt')
df.add_state('living with response')
df.add_state('living with appraisal')
df.add_state('living with spouse')
df.add_state('living with roommate')

df.add_system_transition('living with prompt', 'living with response',
                         '"so, who do you live with?"')
df.add_user_transition('living with response', 'living with spouse',
                       '[{[!my $livingwith=$partnertype=#ONT(partner)], [!a $partnertype=#ONT(partner)]}]')
df.add_user_transition('living with response', 'living with roommate',
                       '[$livingwith=#EXP(roommate)]')
df.add_user_transition('living with response', 'living with friend',
                       '[friend]')
df.add_user_transition('living with response', 'living with parents',
                       '[]')

# personality
df.add_state('personality')

if __name__ == '__main__':
    df.set_state('living with prompt')
    df.run(debugging=True)

