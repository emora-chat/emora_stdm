
from emora_stdm import DialogueFlow, NatexNLU, NatexNLG, Macro


df = DialogueFlow(initial_state="start", kb='family.json')

# living with
df.add_state('living with prompt')
df.add_state('living with response', error_successor='living with unsure')

df.add_state('living with unsure')

df.add_state('living with spouse')
df.add_state('living with roommate')
df.add_state('living with parents')
df.add_state('living with friend')
df.add_state('living with child')
df.add_state('living alone')

df.add_state('personality prompt')
df.add_state('personality unsure')
df.add_state('personality', error_successor='personality unsure')
df.add_state('alone prompt')

df.add_state('smart')
df.add_state('funny')
df.add_state('outgoing')
df.add_state('shy')
df.add_state('polite')
df.add_state('conceited')
df.add_state('good')
df.add_state('athletic')
df.add_state('lazy')
df.add_state('annoying')
df.add_state('hard working')
df.add_state('fun')
df.add_state('worrying')

df.add_state('smart reaction')
df.add_state('funny reaction')
df.add_state('outgoing reaction')
df.add_state('shy reaction')
df.add_state('polite reaction')
df.add_state('conceited reaction')
df.add_state('good reaction')
df.add_state('athletic reaction')
df.add_state('lazy reaction')
df.add_state('annoying reaction')
df.add_state('hard working reaction')
df.add_state('fun reaction')
df.add_state('worrying reaction')

df.add_state('end', error_successor='end')

df.add_system_transition('living with prompt', 'living with response',
                         '"so, who do you live with?"')

df.add_system_transition('living with unsure', 'living with response', '"I didnt catch that, who did you say you live with?"')

df.add_user_transition('living with response', 'living with spouse',
                       '[{[!my $livingwith=$partnertype=#ONT(partner)], [have, $partnertype=#ONT(partner)]}]')
df.add_user_transition('living with response', 'living with roommate',
                       '[$livingwith=#EXP(roommate)]')
df.add_user_transition('living with response', 'living with friend',
                       '[!#SET($livingwith=friend) [friend]]')
df.add_user_transition('living with response', 'living with parents',
                       '[$livingwith=#ONT(parent)]')
df.add_user_transition('living with response', 'living with child',
                       '[$livingwith=#EXP(child)]')
df.add_user_transition('living with response', 'living alone',
                       [
                           '[{alone, by myself, solo, nobody, noone, no one}]',
                           '[!#NOT(negation), [{living, live, with, #EXP(anyone)}]]'
                       ])
df.add_system_transition('living with spouse', 'personality', '[!what is your $partnertype "like?"]')
df.add_system_transition('living with roommate', 'personality', '[!what is your $livingwith "like?"]')
df.add_system_transition('living with friend', 'personality', '[!what is your $livingwith "like?"]')
df.add_system_transition('living with parents', 'personality', '[!what is your $livingwith "like?"]')
df.add_system_transition('living with child', 'personality', '[!what is your $livingwith "like?"]')

df.add_system_transition('living alone', 'alone prompt', '"Do you like living alone?"')
df.add_user_transition('alone prompt', 'end', "Sure, just remember you can always talk to me if you feel lonely. Ill annoy you just as well as any roommate can.")

df.add_system_transition('personality unsure', 'personality', '"Sorry, what is your $livingwith like?"')
df.add_system_transition('personality unsure', 'end', '"Ok, gotcha."')

df.add_user_transition('personality', 'smart', '[{#EXP(smart), #EXP(smart)}]')
df.add_user_transition('personality', 'funny', '[{#EXP(funny)}]')
df.add_user_transition('personality', 'outgoing', '[{#EXP(outgoing)}]')
df.add_user_transition('personality', 'shy', '[{#EXP(shy)}]')
df.add_user_transition('personality', 'polite', '[{#EXP(polite)}]')
df.add_user_transition('personality', 'conceited', '[#EXP(conceited)]')
df.add_user_transition('personality', 'good', '[{good, cool, great, awesome}]')
df.add_user_transition('personality', 'athletic', '[{athletic, sports, works out}]')
df.add_user_transition('personality', 'lazy', '[lazy]')
df.add_user_transition('personality', 'annoying', '[annoying]')
df.add_user_transition('personality', 'hard working', '[hard working]')
df.add_user_transition('personality', 'fun', '[{fun, carefree}]')
df.add_user_transition('personality', 'worrying', '[{worries, worrying, worrisome}]')

df.add_system_transition('smart', 'end', '"I wish I was smart"')
df.add_system_transition('funny', 'end', '"Its good to live with a sense of humor"')
df.add_system_transition('outgoing', 'end', '"Ok. I think its nice to be around someone who is outgoing"')
df.add_system_transition('shy', 'end', '"Some people just like keeping to themselves"')
df.add_system_transition('polite', 'end', '"Yeah. I think having good manners is important"')
df.add_system_transition('conceited', 'end', '"Oh. Confidence is good, but some people take themselves too seriously."')
df.add_system_transition('good', 'end', '"Great, I am happy youre living with someone you appreciate."')
df.add_system_transition('athletic', 'end', '"It sounds like theyre really healthy."')
df.add_system_transition('lazy', 'end', '"Sometimes taking life slow can be good, but adopting responsibility in life is important too."')
df.add_system_transition('annoying', 'end', '"Oh no, I hope you keep your sanity."')
df.add_system_transition('hard working', 'end', '"thats admirable but sometimes it can be good to take life slow too"')
df.add_system_transition('fun', 'end', '"Thats great, spending time with people who are fun like that is great"')
df.add_system_transition('worrying', 'end', '"I see. I think its hard to be stressed all the time."')

df.add_system_transition('end', 'end', '"okay then"')

if __name__ == '__main__':
    df.set_state('living with prompt')
    df.run(debugging=True)

































