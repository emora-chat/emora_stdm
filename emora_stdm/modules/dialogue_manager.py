print('beginning imports...')
import os, random
from emora_stdm import DialogueFlow, Macro, NatexNLU, NOT
from emora_stdm.state_transition_dialogue_manager.composite_dialogue_flow import CompositeDialogueFlow
from modules.opening import component as opening
from modules.hobby import ResetLoop, df as hobby, State as hobby_states
from modules.pets import df as pet, State as pet_states
from modules.family_loop import df as family
from modules.stop_conversation import stop_nlu, df as stop, State as stop_states
print('finished imports...')

def add_global_nlu_to_components(components, state, nlu, score=10.0):
    if isinstance(state, tuple):
        origin_name = state[0]
    else:
        origin_name = 'SYSTEM'
    for name,component in components.items():
        if origin_name == 'SYSTEM' or origin_name != name:
            if component.has_state(state):
                component.update_state_settings(state, global_nlu=nlu)
            else:
                component.add_state(state, global_nlu=nlu)
            for source, target, trans in component.incoming_transitions(state):
                if 'global' in component._graph.arc_data(source,target,trans):
                    component.update_transition_settings(source,target,trans, score=score)

def add_macros_to_components(components, macros):
    for name,component in components.items():
        component._macros.update(macros)

def add_knowledge_to_components(components, knowledge_files):
    for origin_name,file in knowledge_files:
        for name,component in components.items():
            if origin_name != name:
                component._kb.load_json_file(file)

AVAILABLE = {'movies','music','sports','news','pet','hobby','family'}

class DMAvailable(Macro):
    def run(self, ngrams, vars, args):
        available = set(AVAILABLE)
        if 'dm_not_available' in vars:
            available = available - vars['dm_not_available']
        if args[0] in available:
            return True
        return False

class DMNotAvailable(Macro):
    def run(self, ngrams, vars, args):
        if 'dm_not_available' in vars:
            for arg in args:
                if arg not in vars['dm_not_available']:
                    return False
            return True
        return False

class DMUpdateNotAvailable(Macro):
    def run(self, ngrams, vars, args):
        if 'dm_not_available' not in vars:
            vars['dm_not_available'] = set()
        vars['dm_not_available'].add(args[0])

class SetTopicSuggestion(Macro):
    def run(self, ngrams, vars, args):
        vars['dm_suggested_topic'] = str(args[0])

class CheckExternalComp(Macro):
    def run(self, ngrams, vars, args):
        if 'chosenModule' in vars:
            if vars['chosenModule'] == args[0]:
                return True
        return False

class ChooseTransitionOut(Macro):
    def run(self, ngrams, vars, args):
        opts = TRANSITIONS
        if 'transition_out' in vars:
            opts = opts - {vars['transition_out']}
        return random.choice(tuple(opts))


macros = {"DMAvailable":DMAvailable(), "DMNotAvailable":DMNotAvailable(), "DMUpdateNotAvailable":DMUpdateNotAvailable(),
          "SetTopicSuggestion":SetTopicSuggestion(), "CheckExternalComp":CheckExternalComp(), "ChooseTransitionOut": ChooseTransitionOut(),
          "ResetLoop": ResetLoop()}

cdf = CompositeDialogueFlow('start', initial_speaker=DialogueFlow.Speaker.USER, macros=macros, system_error_state='topic_master', user_error_state='topic_master')
cdf.add_component(opening, 'opening')
cdf.add_user_transition('start', ('opening', 'prestart'), '/.*/')
cdf.controller().update_state_settings(('opening', 'prestart'), user_multi_hop=True)

cdf.add_state('topic_master', 'topic_master')
cdf.controller().update_state_settings('topic_master', system_multi_hop=True, memory=0)
cdf.add_state('get_to_know_intro')
cdf.add_state('intermediate_topic_switch')
opening.add_system_transition('transition_out', ('SYSTEM', 'get_to_know_intro'), '')
opening.update_state_settings(('SYSTEM', 'get_to_know_intro'), system_multi_hop=True)

cdf.add_system_transition('get_to_know_intro', 'topic_master', '"I want to get to know you a bit better so we can talk about things you are interested in."')
cdf.add_system_transition('intermediate_topic_switch', 'topic_master', '"Let\'s see. "')
cdf.controller().update_state_settings('get_to_know_intro', system_multi_hop=True)
cdf.controller().update_state_settings('intermediate_topic_switch', system_multi_hop=True)

cdf.add_component(hobby, 'hobby')
cdf.add_system_transition('topic_master', 'hobby_intro', '[!#DMAvailable(hobby) " "]')
cdf.add_system_transition('hobby_intro', ('hobby', hobby_states.PICK_GENRE), '[!#DMUpdateNotAvailable(hobby)]')
cdf.controller().update_state_settings('hobby_intro', system_multi_hop=True)
cdf.controller().update_state_settings(('hobby', hobby_states.PICK_GENRE), system_multi_hop=True)
hobby.add_system_transition(hobby_states.TRANSITION_OUT, ('SYSTEM', 'intermediate_topic_switch'), '[!"I have really enjoyed talking about these inventions with you."]')
hobby.update_state_settings(('SYSTEM', 'intermediate_topic_switch'), system_multi_hop=True)

cdf.add_component(pet, 'pet')
cdf.add_system_transition('topic_master', 'pet_intro', '[!#DMAvailable(pet)]')
cdf.add_system_transition('pet_intro', ('pet', pet_states.START_PET), '[!#DMUpdateNotAvailable(pet)]')
cdf.controller().update_state_settings('pet_intro', system_multi_hop=True)
cdf.controller().update_state_settings(('pet', pet_states.START_PET), system_multi_hop=True)
pet.add_system_transition(pet_states.END, ('SYSTEM', 'intermediate_topic_switch'), '[!"I have really liked learning about your experiences with pets."]')
pet.update_state_settings(('SYSTEM', 'intermediate_topic_switch'), system_multi_hop=True)

cdf.add_component(family, 'family')
cdf.add_system_transition('topic_master', 'family_intro', '[!#DMAvailable(family)]', score=10.0)
cdf.add_system_transition('family_intro', ('family', 'root'), '[!#DMUpdateNotAvailable(family)]')
cdf.controller().update_state_settings('family_intro', system_multi_hop=True)
cdf.controller().update_state_settings(('family', 'root'), system_multi_hop=True)
family.add_system_transition('end', ('SYSTEM', 'intermediate_topic_switch'), '[!"It was interesting to learn more about the people in your life."]')
family.update_state_settings(('SYSTEM', 'intermediate_topic_switch'), system_multi_hop=True)

cdf.add_component(stop, 'stop')
add_global_nlu_to_components(cdf._components, ('stop', stop_states.REC_OFF), stop_nlu)
stop.add_system_transition(stop_states.END, ('SYSTEM', 'intermediate_topic_switch'), '')
stop.update_state_settings(('SYSTEM', 'intermediate_topic_switch'), system_multi_hop=True)

########################
# External components
########################

cdf.controller().add_system_transition('topic_master', 'movies_intro', '[!#DMAvailable(movies) "<<movies>> I think watching movies is a great way to relax and have fun."]')
cdf.controller().add_system_transition('movies_intro', 'movies', '[!#DMUpdateNotAvailable(movies) #SetTopicSuggestion(movies) " "]')
cdf.controller().update_state_settings('movies_intro', system_multi_hop=True)
cdf.controller().add_user_transition('movies', 'movies', '#CheckExternalComp(movies)')
cdf.controller().set_error_successor('movies', 'intermediate_topic_switch')
cdf.controller().add_system_transition('movies', 'movies', '[!#DMUpdateNotAvailable(movies) #SetTopicSuggestion(movies) "<<movies>> I think watching movies is a great way to relax and have fun."]')

cdf.controller().add_system_transition('topic_master', 'music_intro', '[!#DMAvailable(music) "<<music>> Listening to music can is so much fun."]')
cdf.controller().add_system_transition('music_intro', 'music', '[!#DMUpdateNotAvailable(music) #SetTopicSuggestion(music) " "]')
cdf.controller().update_state_settings('music_intro', system_multi_hop=True)
cdf.controller().add_user_transition('music', 'music', '#CheckExternalComp(music)')
cdf.controller().set_error_successor('music', 'intermediate_topic_switch')
cdf.controller().add_system_transition('music', 'music', '[!#DMUpdateNotAvailable(music) #SetTopicSuggestion(music) "<<music>> Listening to music can is so much fun."]')

cdf.controller().add_system_transition('topic_master', 'news_intro', '[!#DMAvailable(news) "<<news>> There are always interesting new events happening every day."]')
cdf.controller().add_system_transition('news_intro', 'news', '[!#DMUpdateNotAvailable(news) #SetTopicSuggestion(news) " "]')
cdf.controller().update_state_settings('news_intro', system_multi_hop=True)
cdf.controller().add_user_transition('news', 'news', '#CheckExternalComp(news)')
cdf.controller().set_error_successor('news', 'intermediate_topic_switch')
cdf.controller().add_system_transition('news', 'news', '[!#DMUpdateNotAvailable(news) #SetTopicSuggestion(news) "<<news>> There are always interesting new events happening every day."]')

cdf.controller().add_system_transition('topic_master', 'sports_intro', '[!#DMAvailable(sports) "<<nba>> I think both watching and playing sports are a good way to have fun."]')
cdf.controller().add_system_transition('sports_intro', 'sports', '[!#DMUpdateNotAvailable(sports) #SetTopicSuggestion(nba) " "]')
cdf.controller().update_state_settings('sports_intro', system_multi_hop=True)
cdf.controller().add_user_transition('sports', 'sports', '#CheckExternalComp(nba)')
cdf.controller().set_error_successor('sports', 'intermediate_topic_switch')
cdf.controller().add_system_transition('sports', 'sports', '[!#DMUpdateNotAvailable(sports) #SetTopicSuggestion(nba) "<<nba>> I think both watching and playing sports are a good way to have fun."]')

TRANSITIONS = {"I\'ve recently started learning about sports, but I also know a lot about movies and music.",
                 "Music and sports seem to be popular topics, but I also enjoy talking about movies.",
                 "Movies and sports are getting a lot of requests, but I also like talking about music.",
                 "I enjoy learning about your taste in movies and music, but I also like talking about sports.",
                 "I\'ve recently started learning about pets, but I also know a lot about movies and music.",
                 "Music and pets seem to be popular topics, but I also enjoy talking about movies.",
                 "Movies and sports are getting a lot of requests, but I also like talking about pets.",
                 "I enjoy learning about your opinions on movies and pets, but I also like talking about sports."
               }
transition_out = '[! "What would you like to talk about next? " $transition_out=#ChooseTransitionOut()]'
cdf.controller().add_system_transition('topic_master', 'no_options', transition_out, score=0.0)

movies_str = '{movie,movies,film,films,tv,shows,television}'
music_str = '{music,song,songs,melody,melodies,album,albums,concert,concerts}'
news_str = '{news,politics,technology,business,events}'
sports_str = '{sport,sports,athletics,basketball,football,hockey,golf,tennis}'
pet_str = '{pet,pets,animals,animal,cat,cats,dog,dogs}'
hobby_str = '{hobby,hobbies,activity,activities,fun things,things to do,pasttimes}'
# family = ''
no_options_choice = '[#NOT(dont like,dislike,detest,bored,uninterested,hate,dont want,not),%s]'

cdf.controller().add_user_transition('no_options', 'movies_intro', no_options_choice%movies_str)
cdf.controller().add_user_transition('no_options', 'music_intro', no_options_choice%music_str)
cdf.controller().add_user_transition('no_options', 'news_intro', no_options_choice%news_str)
cdf.controller().add_user_transition('no_options', 'sports_intro', no_options_choice%sports_str)
cdf.controller().add_user_transition('no_options', 'pet_intro', no_options_choice%pet_str)
cdf.controller().add_user_transition('no_options', 'hobby_intro', no_options_choice%hobby_str)
cdf.controller().set_error_successor('no_options', 'intermediate_topic_switch')



########################
# Global NLU to all components
########################


chat_question = '[{can,will,could,lets,let us}?, {chat,talk,discuss,converse,conversation,discussion, tell me}, %s]'
know_question = '[{do you know, have you heard}, %s]'
think_question = '[what, {think,opinion,favorite,best,recent,know}, %s]'

add_global_nlu_to_components(cdf._components, ('SYSTEM','movies'), [chat_question % movies_str, know_question % movies_str, think_question % movies_str])
add_global_nlu_to_components(cdf._components, ('SYSTEM','music'), [chat_question%music_str,know_question%music_str,think_question%music_str])
add_global_nlu_to_components(cdf._components, ('SYSTEM','sports'), [chat_question%sports_str,know_question%sports_str,think_question%sports_str])
add_global_nlu_to_components(cdf._components, ('SYSTEM','news'), [chat_question%news_str,know_question%news_str,think_question%news_str])
add_global_nlu_to_components(cdf._components, ('pet', pet_states.START_PET), [chat_question%pet_str,know_question%pet_str,think_question%pet_str])
add_global_nlu_to_components(cdf._components, ('hobby', hobby_states.FIRST_ASK_HOBBY), [chat_question%hobby_str,know_question%hobby_str,think_question%hobby_str])
hobby.add_system_transition(hobby_states.ACK_END, ('SYSTEM', 'intermediate_topic_switch'), '[!"This has been great. Ive learned some new things and some new activities I may end up trying."]')

#add_global_nlu_to_components(cdf._components, ('family', 'root'), '[[!my $related_type={#ONT(person),#EXP(roommate),family}]]')

general_topic_switch = '[{can,will,could,lets,let us}?, {chat,talk,discuss,converse,conversation,discussion}, {else,different,other,new,another}]'
add_global_nlu_to_components(cdf._components, ('SYSTEM','intermediate_topic_switch'), general_topic_switch, score=9.0)

########################
# Distribute Knowledge to all components
########################

add_macros_to_components(cdf._components, macros)
add_knowledge_to_components(cdf._components, [('hobby',os.path.join('modules',"hobbies.json")),
                                              ('family',os.path.join('modules',"family.json")),
                                              ('stop',os.path.join('modules', "stop_convo.json"))])

cdf.precache_transitions()
########################
# Testing
########################

import json, time
from emora_stdm import HashableDict
from collections import defaultdict, deque

PUBLIC_ENUMS = {
    'Speaker': DialogueFlow.Speaker
}

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) in PUBLIC_ENUMS.values():
            return {"__enum__": str(obj)}
        return json.JSONEncoder.default(self, obj)


def as_enum(d):
    if "__enum__" in d:
        name, member = d["__enum__"].split(".")
        return getattr(PUBLIC_ENUMS[name], member)
    else:
        return d

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return {"__set__": list(obj)}
        return json.JSONEncoder.default(self, obj)

def as_set(d):
    if "__set__" in d:
        return set(d["__set__"])
    else:
        return d

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

def first_turn():
    cdf.user_turn("hello", debugging=False)
    intermediate_state = cdf.state()
    response = cdf.system_turn(debugging=False)

def task():
    while True:
        text = input("U: ")
        start = time.time()
        cdf.user_turn(text, debugging=False)
        intermediate_state = cdf.state()
        response = cdf.system_turn(debugging=False)
        final_state = cdf.state()
        print("State after sys trans: %s" % str(final_state))
        print("ELAPSED: ", time.time() - start)

        start = time.time()
        # MEMORY SERIALIZATION
        mem = {}
        for name, component in cdf._components.items():
            mem[name] = {}
            for state in component.graph().nodes():
                encoded_state = encode_state(state)
                mem[name][encoded_state] = [
                    (encode_state(item[0]), encode_state(item[1]), item[2]) if item is not None else None for item in
                    list(component.state_settings(state).memory._data)]
                # for item in list(component.state_settings(state).memory._data):
                #     if item is not None:
                #         new_tup = (encode_state(item[0]),encode_state(item[1]),item[2])
                #         mem[name][encoded_state].append(new_tup)
                #     else:
                #         mem[name][encoded_state].append(None)
        saved_mem = json.dumps(mem, cls=EnumEncoder)

        # GATE SERIALIZATION
        json_gates = {}
        for name, component in cdf._components.items():
            json_gates[name] = {
                encode_state(trans[0]) + "||" + encode_state(trans[1]) + "||" + str(trans[2]): hash_dicts for
                trans, hash_dicts in component.gates().items()}
            # for trans,hash_dicts in component.gates().items():
            #     new_tup = encode_state(trans[0]) + "||" + encode_state(trans[1]) + "||" + str(trans[2])
            #     json_gates[name][new_tup] = hash_dicts
        json_gates = json.dumps(json_gates, cls=SpecializedEncoder)
        print("SERIAL ELAPSED: ", time.time() - start)

        start = time.time()
        #DESERIALIZATION
        if saved_mem is not None:
            saved_mem = json.loads(saved_mem, object_hook=as_enum)
            for name, mem in saved_mem.items():
                component = cdf.component(name)
                for state in component.graph().nodes():
                    encoded_state = encode_state(state)
                    decoded_trans = [
                        (decode_state(item[0]), decode_state(item[1]), item[2]) if item is not None else None for item
                        in mem[encoded_state]]
                    # for item in mem[encoded_state]:
                    #     if item is not None:
                    #         decoded_trans.append()
                    #     else:
                    #         decoded_trans.append(None)
                    component.state_settings(state).memory._data = deque(decoded_trans)
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
        print("DESERIAL ELAPSED: ", time.time() - start)

        print("S: %s"%response)

if __name__ == '__main__':
    # movies_str = '{movie,movies,film,films,tv,shows,television}'
    # music_str = '{music,song,songs,melody,melodies,album,albums,concert,concerts}'
    # news_str = '{news,politics,technology,business,events}'
    # sports_str = '{sport,sports,athletics,basketball,football,hockey,golf,tennis}'
    # pet_str = '{pet,pets,animals,animal,cat,cats,dog,dogs}'
    # hobby_str = '{hobby,hobbies,activity,activities,fun things,things to do,pasttimes}'
    # # family = ''
    # no_options_choice = '[#NOT(dont like,dislike,detest,bored,uninterested,hate,dont want,not),%s]'
    #
    # n = NatexNLU(no_options_choice%movies_str, macros={"NOT":NOT()})
    # print(n.match("i do not like movies"))
    # print(n.match("not movies"))
    # print(n.match("i would rather not talk about movies"))
    # print(n.match("i dont want to talk about movies"))
    # print(n.match("movies"))
    # print(n.match("i would like to talk about movies"))
    # print(n.match("i do like movies too"))

    cdf.run(debugging=True)

    # import cProfile
    # cProfile.run('first_turn()')