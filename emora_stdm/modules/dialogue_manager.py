print('beginning imports...')
import os, random
from emora_stdm import DialogueFlow, Macro
from emora_stdm.state_transition_dialogue_manager.composite_dialogue_flow import CompositeDialogueFlow
from modules.opening import component as opening
from modules.hobby import df as hobby
from modules.hobby import State as hobby_states
from modules.pets import df as pet
from modules.pets import State as pet_states
from modules.family import df as family
from modules.stop_conversation import df as stop
from modules.stop_conversation import State as stop_states
from modules.stop_conversation import stop_nlu
print('finished imports...')

def add_global_nlu_to_components(components, state, nlu, knowledge_file=None):
    for name,component in components.items():
        if knowledge_file is not None:
            component._kb.load_json_file(knowledge_file)
        if component.has_state(state):
            component.update_state_settings(state, global_nlu=nlu)
        else:
            component.add_state(state, global_nlu=nlu)

def add_macros_to_components(components, macros):
    for name,component in components.items():
        component._macros.update(macros)

class DMAvailable(Macro):
    def run(self, ngrams, vars, args):
        if 'dm_not_available' in vars:
            if args[0] not in vars['dm_not_available']:
                return True
            return False
        return True

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

class GetTopicSuggestions(Macro):
    def run(self, ngrams, vars, args):
        options = vars['dm_available']
        if 'dm_not_available' in vars:
            options = options - vars['dm_not_available']
        if len(options) > 0:
            vars['dm_suggested_topic'] = random.choice(tuple(options))
            return vars['dm_suggested_topic']
        else:
            return False

class IsTopicSuggestion(Macro):
    def run(self, ngrams, vars, args):
        if 'dm_suggested_topic' in vars and args[0] == vars["dm_suggested_topic"]:
            return True
        return False

macros = {"DMAvailable":DMAvailable(), "DMNotAvailable":DMNotAvailable(), "DMUpdateNotAvailable":DMUpdateNotAvailable(),
          "GetTopicSuggestions":GetTopicSuggestions(), "IsTopicSuggestion":IsTopicSuggestion()}

cdf = CompositeDialogueFlow('start', initial_speaker=DialogueFlow.Speaker.USER, macros=macros)
cdf.controller()._kb.load_json_file(os.path.join('modules',"hobbies.json"))
cdf.set_vars({'dm_available': {'movies','music','sports','news','pet','hobby'}})
cdf.add_component(opening, 'opening')
cdf.add_user_transition('start', ('opening', 'prestart'), '/.*/')
cdf.controller().update_state_settings(('opening', 'prestart'), user_multi_hop=True)

cdf.add_state('topic_master', 'topic_master')
cdf.controller().update_state_settings('topic_master', system_multi_hop=True, memory=0)
cdf.add_state('get_to_know_intro')
cdf.add_state('intermediate_topic_switch')
opening.add_system_transition('transition_out', ('SYSTEM', 'get_to_know_intro'), '"."')
opening.update_state_settings(('SYSTEM', 'get_to_know_intro'), system_multi_hop=True)

cdf.add_system_transition('get_to_know_intro', 'topic_master', '"I want to get to know you a bit better so we can talk about things you are interested in. So, let\'s see."')
cdf.add_system_transition('intermediate_topic_switch', 'topic_master', '"So, "')
cdf.controller().update_state_settings('get_to_know_intro', system_multi_hop=True)
cdf.controller().update_state_settings('intermediate_topic_switch', system_multi_hop=True)

cdf.add_component(hobby, 'hobby')
cdf.add_system_transition('topic_master', 'hobby_intro', '[!#DMAvailable(hobby) "."]')
cdf.add_system_transition('hobby_intro', ('hobby', hobby_states.INTRO_READING), '[!#DMUpdateNotAvailable(hobby) "."]')
cdf.controller().update_state_settings('hobby_intro', system_multi_hop=True)
cdf.controller().update_state_settings(('hobby', hobby_states.INTRO_READING), system_multi_hop=True)
hobby.add_system_transition(hobby_states.TRANSITION_OUT, ('SYSTEM', 'intermediate_topic_switch'), '[!"I have really enjoyed talking about these inventions with you."]')
hobby.update_state_settings(('SYSTEM', 'intermediate_topic_switch'), system_multi_hop=True)

cdf.add_component(pet, 'pet')
cdf.add_system_transition('topic_master', 'pet_intro', '[!#DMAvailable(pet) "."]')
cdf.add_system_transition('pet_intro', ('pet', pet_states.PETS_Y), '[!#DMUpdateNotAvailable(pet) "."]')
cdf.controller().update_state_settings('pet_intro', system_multi_hop=True)
cdf.controller().update_state_settings(('pet', pet_states.PETS_Y), system_multi_hop=True)
pet.add_system_transition(pet_states.END, ('SYSTEM', 'intermediate_topic_switch'), '[!"I have really liked learning about your experiences with pets."]')
pet.update_state_settings(('SYSTEM', 'intermediate_topic_switch'), system_multi_hop=True)

# cdf.add_component(family, 'family')
# cdf.add_system_transition('topic_master', ('family', hobby_states.INTRO_READING), '"."')
# cdf.controller().update_state_settings(('family', hobby_states.INTRO_READING), system_multi_hop=True)
# family.add_system_transition(hobby_states.TRANSITION_OUT, ('SYSTEM', 'topic_master'), '"."')
# family.update_state_settings(('SYSTEM', 'topic_master'), system_multi_hop=True)

cdf.add_component(stop, 'stop')
add_global_nlu_to_components(cdf._components, ('stop', stop_states.REC_OFF), stop_nlu, os.path.join('modules', "stop_convo.json"))
stop.add_system_transition(stop_states.END, ('SYSTEM', 'topic_master'), '"."')


########################
# External components
########################

cdf.controller().add_system_transition('topic_master', 'movies', '[!#DMAvailable(movies) "movies stub."]')
cdf.controller().add_user_transition('movies', 'intermediate_topic_switch', '[!/.*/ #DMUpdateNotAvailable(movies)]')
cdf.controller().add_system_transition('movies', 'movies', '[!#DMUpdateNotAvailable(movies) "movies stub."]')

cdf.controller().add_system_transition('topic_master', 'music', '[!#DMAvailable(music) "music stub."]')
cdf.controller().add_user_transition('music', 'intermediate_topic_switch', '[!/.*/ #DMUpdateNotAvailable(music)]')
cdf.controller().add_system_transition('music', 'music', '[!#DMUpdateNotAvailable(music) "music stub."]')

cdf.controller().add_system_transition('topic_master', 'news', '[!#DMAvailable(news) "news stub."]')
cdf.controller().add_user_transition('news', 'intermediate_topic_switch', '[!/.*/ #DMUpdateNotAvailable(news)]')
cdf.controller().add_system_transition('news', 'news', '[!#DMUpdateNotAvailable(news) "news stub."]')

cdf.controller().add_system_transition('topic_master', 'sports', '[!#DMAvailable(sports) "sports stub."]')
cdf.controller().add_user_transition('sports', 'intermediate_topic_switch', '[!/.*/ #DMUpdateNotAvailable(sports)]')
cdf.controller().add_system_transition('sports', 'sports', '[!#DMUpdateNotAvailable(sports) "sports stub."]')

cdf.controller().add_system_transition('topic_master', 'no_options', '"We can talk about different things like movies, music, or sports."', score=0.0)
cdf.controller().set_error_successor('no_options', 'intermediate_topic_switch')


########################
# Global NLU tp all components
########################

add_global_nlu_to_components(cdf._components, ('SYSTEM','movies'), '[{movie,movies,film,films,tv,shows,television}]')
add_global_nlu_to_components(cdf._components, ('SYSTEM','music'), '[{music,song,songs,melody,melodies,album,albums,concert,concerts}]')
add_global_nlu_to_components(cdf._components, ('SYSTEM','sports'), '[{sport,sports,athletics,basketball,football,hockey,golf,tennis}]')
add_global_nlu_to_components(cdf._components, ('SYSTEM','news'), '[{news}]')
add_global_nlu_to_components(cdf._components, ('pet', pet_states.PETS_Y), '[{pet,pets,animals,animal,cat,cats,dog,dogs}]')
add_global_nlu_to_components(cdf._components, ('hobby', hobby_states.INTRO_READING), '[{hobby,hobbies,activity,activities,fun things,things to do,pasttimes}]')

########################
# Macros to all components
########################

add_macros_to_components(cdf._components, macros)

########################
# Testing
########################

if __name__ == '__main__':
    cdf.run(debugging=True)