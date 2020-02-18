print('beginning imports...')
import os, random
from emora_stdm import DialogueFlow, Macro
from emora_stdm.state_transition_dialogue_manager.composite_dialogue_flow import CompositeDialogueFlow
from modules.opening import component as opening
from modules.hobby import df as hobby
from modules.hobby import State as hobby_states
from modules.pets import df as pet
from modules.pets import State as pet_states
from modules.family_loop import df as family
from modules.stop_conversation import df as stop
from modules.stop_conversation import State as stop_states
from modules.stop_conversation import stop_nlu
print('finished imports...')

def add_global_nlu_to_components(components, state, nlu):
    if isinstance(state, tuple):
        origin_name = state[0]
    else:
        origin_name = 'SYSTEM'
    for name,component in components.items():
        if origin_name != name:
            if component.has_state(state):
                component.update_state_settings(state, global_nlu=nlu)
            else:
                component.add_state(state, global_nlu=nlu)

def add_macros_to_components(components, macros):
    for name,component in components.items():
        component._macros.update(macros)

def add_knowledge_to_components(components, knowledge_files):
    for origin_name,file in knowledge_files:
        for name,component in components.items():
            if origin_name != name:
                component._kb.load_json_file(file)

class DMAvailable(Macro):
    def run(self, ngrams, vars, args):
        available = vars['dm_available']
        if 'dm_not_available' in vars:
            available = vars['dm_available'] - vars['dm_not_available']
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
          "SetTopicSuggestion":SetTopicSuggestion(), "CheckExternalComp":CheckExternalComp(), "ChooseTransitionOut": ChooseTransitionOut()}

cdf = CompositeDialogueFlow('start', initial_speaker=DialogueFlow.Speaker.USER, macros=macros)
#cdf.set_vars({'dm_available': {'movies','music','sports','news','pet','hobby'}})
cdf.set_vars({'dm_available': {'hobby', 'pet', 'family'}})
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
cdf.add_system_transition('intermediate_topic_switch', 'topic_master', '"Um, "')
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
cdf.add_system_transition('topic_master', 'family_intro', '[!#DMAvailable(family)]')
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

cdf.controller().add_system_transition('topic_master', 'movies_intro', '[!#DMAvailable(movies) "<<movies>> movies stub."]')
cdf.controller().add_system_transition('movies_intro', 'movies', '[!#DMUpdateNotAvailable(movies) #SetTopicSuggestion(movies) " "]')
cdf.controller().update_state_settings('movies_intro', system_multi_hop=True)
cdf.controller().add_user_transition('movies', 'movies', '#CheckExternalComp(movies)')
cdf.controller().set_error_successor('movies', 'intermediate_topic_switch')
cdf.controller().add_system_transition('movies', 'movies', '[!#DMUpdateNotAvailable(movies) #SetTopicSuggestion(movies) "<<movies>> movies stub."]')

cdf.controller().add_system_transition('topic_master', 'music_intro', '[!#DMAvailable(music) "<<music>> music stub."]')
cdf.controller().add_system_transition('music_intro', 'music', '[!#DMUpdateNotAvailable(music) #SetTopicSuggestion(music) " "]')
cdf.controller().update_state_settings('music_intro', system_multi_hop=True)
cdf.controller().add_user_transition('music', 'music', '#CheckExternalComp(music)')
cdf.controller().set_error_successor('music', 'intermediate_topic_switch')
cdf.controller().add_system_transition('music', 'music', '[!#DMUpdateNotAvailable(music) #SetTopicSuggestion(music) "<<music>> music stub."]')

cdf.controller().add_system_transition('topic_master', 'news_intro', '[!#DMAvailable(news) "<<news>> news stub."]')
cdf.controller().add_system_transition('news_intro', 'news', '[!#DMUpdateNotAvailable(news) #SetTopicSuggestion(news) " "]')
cdf.controller().update_state_settings('news_intro', system_multi_hop=True)
cdf.controller().add_user_transition('news', 'news', '#CheckExternalComp(news)')
cdf.controller().set_error_successor('news', 'intermediate_topic_switch')
cdf.controller().add_system_transition('news', 'news', '[!#DMUpdateNotAvailable(news) #SetTopicSuggestion(news) "<<news>> news stub."]')

cdf.controller().add_system_transition('topic_master', 'sports_intro', '[!#DMAvailable(sports) "<<sports>> sports stub."]')
cdf.controller().add_system_transition('sports_intro', 'sports', '[!#DMUpdateNotAvailable(sports) #SetTopicSuggestion(sports) " "]')
cdf.controller().update_state_settings('sports_intro', system_multi_hop=True)
cdf.controller().add_user_transition('sports', 'sports', '#CheckExternalComp(sports)')
cdf.controller().set_error_successor('sports', 'intermediate_topic_switch')
cdf.controller().add_system_transition('sports', 'sports', '[!#DMUpdateNotAvailable(sports) #SetTopicSuggestion(sports) "<<sports>> sports stub."]')

TRANSITIONS = {"I\'ve recently started learning about sports, but I also know a lot about movies and music.",
                 "Music and sports seem to be popular topics, but I also enjoy talking about movies.",
                 "Movies and sports are getting a lot of requests, but I also like talking about music.",
                 "I enjoy learning about your taste in movies and music, but I also like talking about sports."}
transition_out = '[! "What would you like to talk about next? " $transition_out=#ChooseTransitionOut()]'
cdf.controller().add_system_transition('topic_master', 'no_options', transition_out, score=0.0)
cdf.controller().set_error_successor('no_options', 'intermediate_topic_switch')


########################
# Global NLU tp all components
########################

add_global_nlu_to_components(cdf._components, ('SYSTEM','movies'), '[{movie,movies,film,films,tv,shows,television}]')
add_global_nlu_to_components(cdf._components, ('SYSTEM','music'), '[{music,song,songs,melody,melodies,album,albums,concert,concerts}]')
add_global_nlu_to_components(cdf._components, ('SYSTEM','sports'), '[{sport,sports,athletics,basketball,football,hockey,golf,tennis}]')
add_global_nlu_to_components(cdf._components, ('SYSTEM','news'), '[{news}]')
add_global_nlu_to_components(cdf._components, ('pet', pet_states.START_PET), '[{pet,pets,animals,animal,cat,cats,dog,dogs}]')
add_global_nlu_to_components(cdf._components, ('hobby', hobby_states.FIRST_ASK_HOBBY), '[{hobby,hobbies,activity,activities,fun things,things to do,pasttimes}]')
add_global_nlu_to_components(cdf._components, ('family', 'root'), '[[!my $related_type={#ONT(person),#EXP(roommate),family}]]')

########################
# Macros to all components
########################

add_macros_to_components(cdf._components, macros)
add_knowledge_to_components(cdf._components, [('hobby',os.path.join('modules',"hobbies.json")),
                                              ('family',os.path.join('modules',"family.json")),
                                              ('stop',os.path.join('modules', "stop_convo.json"))])

########################
# Testing
########################

if __name__ == '__main__':
    cdf.run(debugging=True)

