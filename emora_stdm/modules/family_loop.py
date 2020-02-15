
from emora_stdm import DialogueFlow, NatexNLU, NatexNLG, Macro


df = DialogueFlow(initial_state="root", kb='family.json')


root = 'root'
df.add_state(root, error_successor=root)
df.add_system_transition(root, root, '{yeah, for sure, okay}', score=0)

agree = '[!#NOT(#EXP(negation)) [{i think so, yes, yeah, yea, sure, for sure, yup, yep, i agree, of course, definitely, absolutely, certainly, surely, i would say so}]]'
disagree = '[{i dont think, no, nope, not really, not at all, nah, #EXP(negation)}]'
maybe = '[{maybe, not sure, dont know, sometimes, at times, some of the time, partly, part of the time, kind of, mostly, a little}]'

## related person
df.var_dependencies()['related_type'] = {'related_personality'}

# S: Who do you live with?
root = 'root'
df.add_state('opening live with', error_successor='opening live with repeat')
df.add_system_transition(root, 'opening live with',
'[!#GATE() "So, who do you live with?"]', score=0.001)
df.add_system_transition('opening live with repeat', 'opening live with',
'[!#GATE() "Wait, I didn\'t catch that. Who do you live with?"]')

df.add_system_transition('opening live with repeat', 'live with me',
'[!"Sorry, I do not seem to know who that is. But I guess you live with me in a way, right?"]', score=0.001)

df.add_user_transition('live with me', 'live with me agree', agree)
df.add_user_transition('live with me', 'live with me disagree', disagree)

df.add_system_transition('live with me agree', root, 'Yeah, I really enjoy being your companion. Thanks for inviting me into your home.')
df.add_system_transition('live with me disagree', root, '"You don\'t think so? I see. I guess you are right. I am not really a real person you live with."')

df.add_user_transition('opening live with', root,
'[!#NOT(#EXP(negation)) [{$related_type={#ONT(person),#EXP(roommate),family},people, someone, anyone, guys, girls}]]')

df.add_user_transition('opening live with', 'live alone',
'{[no one], [alone], [none], [myself], [#EXP(negation), {#EXP(roommate), people, someone, anyone}]}')
df.add_state('live alone response', root)
df.add_system_transition('live alone', 'live alone response', '"Sometimes it is nice to live by yourself."')

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

# S: What is $related_type like?
root = 'root'
df.add_state('personality', error_successor='default personality', user_multi_hop=True)
df.add_system_transition(root, 'personality',
                         '[!#GATE(related_type, related_personality:None) "Oh, what is your" $related_type "like?"]')

df.add_system_transition('default personality', root, '"Interesting."')

df.add_user_transition(root, 'personality',
'[my $related_type=#ONTE(related_person) #NOT(#EXP(negation)) $related_personality=#ONTE(personality_trait)]')

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
df.add_user_transition('personality', 'beautiful', '[{beautiful, pretty, gorgeous, hot, sexy}]')

df.add_system_transition('smart', root, '{"A sharp cookie, huh? They say intelligence is the strongest indicator of carrer success, but has little impact on a person\'s happiness."}')
df.add_system_transition('funny', root, '"Its good to live with a sense of humor"')
df.add_system_transition('outgoing', root, '"Ok. I think its nice to be around someone who is outgoing"')
df.add_system_transition('shy', root, '"Some people just like keeping to themselves"')
df.add_system_transition('polite', root, '"Yeah. I think having good manners is important"')
df.add_system_transition('conceited', root, '"Oh. Confidence is good, but some people take themselves too seriously."')
df.add_system_transition('good', root, '"Great, I am happy you\'re with someone you appreciate."')
df.add_system_transition('athletic', root, '"It sounds like theyre really healthy."')
df.add_system_transition('lazy', root, '"Sometimes taking life slow can be good, but adopting responsibility in life is important too."')
df.add_system_transition('annoying', root, '"Oh no, I hope you keep your sanity."')
df.add_system_transition('hard working', root, '"thats admirable but sometimes it can be good to take life slow too"')
df.add_system_transition('fun', root, '"Thats great, spending time with people who are fun like that is great"')
df.add_system_transition('worrying', root, '"I see. I think its hard to be stressed all the time."')
df.add_system_transition('beautiful', root, '"Aww. Its nice you are with someone that you find beauty in."')


# S: Do you get along with your $related_type?
root = 'root'
df.add_state('ask get along', error_successor=root)
df.add_system_transition(root, 'ask get along',
'[!#GATE(related_type, related_get_along:None) "Do you get along with your" $related_type "?"]')

df.add_user_transition('ask get along', 'get along yes', agree)
df.add_user_transition('ask get along', 'get along no', disagree)
df.add_user_transition('ask get along', 'get along maybe', maybe)

df.add_system_transition('get along yes', root,
'"That\'s wonderful. Having a strong relationship with your" $related_type "is so important."')

df.add_system_transition('get along no', root,
'"Oh that\'s a shame. I think your" $related_type "is someone who should be there for you and understand you, and you should be there for them."')

df.add_system_transition('get along maybe', root,
'"Well I think every relationship has its ups and downs. It\'s hard to get along with anyone one hundred percent."')

# S: What is new with your $related_type?
root = 'root'
df.add_state('life event', error_successor='life event default', user_multi_hop=True)
df.add_system_transition(root, 'life event',
'[!#GATE(related_type, related_new_event:None) "So what is new with your" $related_type "?"]')
df.add_system_transition('life event default', root, '"I see."')

df.add_user_transition('life event', 'marriage', '[{married, wedding, proposed, engaged}]')
df.add_user_transition('life event', 'birth', '[{new baby, [had, baby], birth}]')
df.add_user_transition('life event', 'death', '[{funeral, [-almost, died]}]')
df.add_user_transition('life event', 'relocation', '{new house, moved, new apartment}')
df.add_user_transition('life event', 'divorce', '[{divorce, break up, broke up, breaking up, split up, splitting up, separated}]')
df.add_user_transition('life event', 'illness', '[{hospital, sick, stroke, heart attack, cancer}]')
df.add_user_transition('life event', 'new job', '[{promotion, new job, interview, hired}]')
df.add_user_transition('life event', 'fired', '[{fired, quit}]')
df.add_user_transition('life event', 'new partner', '[{romance, date, new #ONTE(partner), started dating, started seeing someone}]')
df.add_user_transition('life event', 'graduation', '[{graduate, graduated, finished school}]')
df.add_user_transition('life event', 'just work', '[{work, working, worked}]')
df.add_user_transition('life event', 'vacation', '[{trip, vacation, cruise}]')
df.add_user_transition('life event', 'retired', '[{retired, retirement, retire}]')

df.add_system_transition('marriage', root, '"Wow, congratulations to the lovely couple. Hearing about new marriage gives me hope for the future."')
df.add_system_transition('birth', root, '"Oh, a baby! Congratulations to the parents."')
df.add_system_transition('death', root, '"Oh. May the departed rest in peace. I\'m sorry for your loss."')
df.add_system_transition('relocation', root, '"Moving, huh? It always sounded like a lot of work to me, but living somewhere you feel like you belong is important."')
df.add_system_transition('divorce', root, '"Mmm. Separating from someone you used to be close to sounds hard. It might be painful, but hopefully it leads to a better future in the long haul."')
df.add_system_transition('illness', root, '"Oh no! One way or another I hope they feel better soon."')
df.add_system_transition('new job', root, '"Wow, that sounds like a serious career advancement. And to think, I just sit around talking to people all day."')
df.add_system_transition('fired', root, '"Well, it may not be ideal, but you know what they say. One door closes, another opens."')
df.add_system_transition('new partner', root, '"Romance, exciting! How great is it to be newly in love."')
df.add_system_transition('graduation', root, '"Congratulations to the graduated!"')
df.add_system_transition('just work', root, '"Probably working too hard."')
df.add_system_transition('vacation', root, '"A relaxing trip somewhere sounds so nice."')
df.add_system_transition('retired', root, '"Wow, finally done with work then. That\'s great, I think people should get to enjoy the last chapters of their life with the freedom to do what they always wanted."')




# Ask $related_type occupation

if __name__ == '__main__':
    df.run(debugging=True)
