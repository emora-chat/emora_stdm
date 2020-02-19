from emora_stdm import NatexNLU

movies = '{movie,movies,film,films,tv,shows,television}'
music = '{music,song,songs,melody,melodies,album,albums,concert,concerts}'
news = '{hobby,hobbies,activity,activities,fun things,things to do,pasttimes}'
sports = '{sport,sports,athletics,basketball,football,hockey,golf,tennis}'
pet = '{pet,pets,animals,animal,cat,cats,dog,dogs}'
hobby = '{hobby,hobbies,activity,activities,fun things,things to do,pasttimes}'
family = ''
chat_question = '[{can,will,could,lets,let us}?, {chat,talk,discuss,converse,conversation,discussion, tell me}, %s]'
know_question = '[{do you know, have you heard}, %s]'
think_question = '[what, {think,opinion,favorite,best,recent}, %s]'

if __name__ == '__main__':
    print()
    n = NatexNLU([chat_question%movies,know_question%movies,think_question%movies])
    print(n.match("lets talk about movies"))
    print(n.match("talk about movies"))
    print(n.match("tell me about movies"))
    print(n.match("do you know movies"))
    print(n.match("can we talk about movies"))
    print(n.match("what is your favorite movie"))
    print(n.match("can we have a conversation about your favorite movie"))

# add_global_nlu_to_components(cdf._components, ('SYSTEM','music'), [chat_question%music,know_question%music,think_question%music])
# add_global_nlu_to_components(cdf._components, ('SYSTEM','sports'), [chat_question%sports,know_question%sports,think_question%sports])
# add_global_nlu_to_components(cdf._components, ('SYSTEM','news'), [chat_question%news,know_question%news,think_question%news])
# add_global_nlu_to_components(cdf._components, ('pet', pet_states.START_PET), [chat_question%pet,know_question%pet,think_question%pet])
# add_global_nlu_to_components(cdf._components, ('hobby', hobby_states.FIRST_ASK_HOBBY), [chat_question%hobby,know_question%hobby,think_question%hobby])
# add_global_nlu_to_components(cdf._components, ('family', 'root'), '[[!my $related_type={#ONT(person),#EXP(roommate),family}]]')