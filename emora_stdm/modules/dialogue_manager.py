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

class Available(Macro):
    def run(self, ngrams, vars, args):
        if 'dm-not_available' in vars:
            if args[0] not in vars['dm-not_available']:
                return True
            return False
        return True

class NotAvailable(Macro):
    def run(self, ngrams, vars, args):
        if 'dm-not_available' in vars:
            for arg in args:
                if arg not in vars['dm-not_available']:
                    return False
            return True
        return False

class UpdateNotAvailable(Macro):
    def run(self, ngrams, vars, args):
        if 'dm-not_available' not in vars:
            vars['dm-not_available'] = set()
        vars['dm-not_available'].add(args[0])

class GetTopicSuggestions(Macro):
    def run(self, ngrams, vars, args):
        options = vars['dm-available']
        if 'dm-not_available' in vars:
            options = options - vars['dm-not_available']
        if len(options) > 0:
            vars['dm-suggested_topic'] = random.choice(tuple(options))
            return vars['dm-suggested_topic']
        else:
            return False

class IsTopicSuggestion(Macro):
    def run(self, ngrams, vars, args):
        if 'dm-suggested_topic' in vars and args[0] == vars["dm-suggested_topic"]:
            return True
        return False

macros = {"Available":Available(), "NotAvailable":NotAvailable(), "UpdateNotAvailable":UpdateNotAvailable(),
          "GetTopicSuggestions":GetTopicSuggestions(), "IsTopicSuggestion":IsTopicSuggestion()}

cdf = CompositeDialogueFlow('start', initial_speaker=DialogueFlow.Speaker.USER, macros=macros, kb=os.path.join('modules',"stop_convo.json"))
cdf.controller()._kb.load_json_file(os.path.join('modules',"hobbies.json"))
cdf.set_vars({'dm-available': {'movies','music','sports','news','pet','hobby'}})
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
cdf.add_system_transition('intermediate_topic_switch', 'topic_master', '"Ok, what else?"')
cdf.controller().update_state_settings('get_to_know_intro', system_multi_hop=True)
cdf.controller().update_state_settings('intermediate_topic_switch', system_multi_hop=True)

cdf.add_component(hobby, 'hobby')
cdf.add_system_transition('topic_master', ('hobby', hobby_states.INTRO_READING), '[! #Available(hobby) #UpdateNotAvailable(hobby) "Ok, so, "]')
cdf.controller().update_state_settings(('hobby', hobby_states.INTRO_READING), system_multi_hop=True)
hobby.add_system_transition(hobby_states.TRANSITION_OUT, ('SYSTEM', 'intermediate_topic_switch'), '"I have really enjoyed talking about these inventions with you. I am interested in learning more about your opinions on other things too!"')
hobby.update_state_settings(('SYSTEM', 'intermediate_topic_switch'), system_multi_hop=True)

cdf.add_component(pet, 'pet')
cdf.add_system_transition('topic_master', ('pet', pet_states.PETS_Y), '[! #Available(pet) #UpdateNotAvailable(pet) "Oh, I know!"]')
cdf.controller().update_state_settings(('pet', pet_states.PETS_Y), system_multi_hop=True)
pet.add_system_transition(pet_states.END, ('SYSTEM', 'intermediate_topic_switch'), '"I have really liked learning about your experiences with pets."')
pet.update_state_settings(('SYSTEM', 'intermediate_topic_switch'), system_multi_hop=True)

# cdf.add_component(family, 'family')
# cdf.add_system_transition('topic_master', ('family', hobby_states.INTRO_READING), '"."')
# cdf.controller().update_state_settings(('family', hobby_states.INTRO_READING), system_multi_hop=True)
# family.add_system_transition(hobby_states.TRANSITION_OUT, ('SYSTEM', 'topic_master'), '"."')
# family.update_state_settings(('SYSTEM', 'topic_master'), system_multi_hop=True)

cdf.add_component(stop, 'stop')
cdf.controller().add_state(('stop', stop_states.REC_OFF), global_nlu=stop_nlu)
stop.add_system_transition(stop_states.END, ('SYSTEM', 'topic_master'), '"."')


########################
# External components
########################

cdf.controller().add_state('movies', global_nlu='[{movie,movies,film,films,tv,shows,television}]')
cdf.controller().add_state('music', global_nlu='[{music,song,songs,melody,melodies,album,albums,concert,concerts}]')
cdf.controller().add_state('sports', global_nlu='[{sport,sports,athletics,basketball,football,hockey,golf,tennis}]')
cdf.controller().add_state('news', global_nlu='[{news}]')
cdf.controller().update_state_settings(('pet', pet_states.PETS_Y), global_nlu='[{pet,pets,animals,animal,cat,cats,dog,dogs}]')
cdf.controller().update_state_settings(('hobby', hobby_states.INTRO_READING), global_nlu='[{hobby,hobbies,activity,activities,fun things,things to do,pasttimes}]')

cdf.controller().add_system_transition('movies', 'topic_master', '[! #UpdateNotAvailable(movies) "Movie stub."]')
cdf.controller().update_state_settings('movies', system_multi_hop=True)
cdf.controller().set_error_successor('movies', 'topic_master')
cdf.controller().add_system_transition('music', 'topic_master', '[! #UpdateNotAvailable(music) "Music stub."]')
cdf.controller().update_state_settings('music', system_multi_hop=True)
cdf.controller().set_error_successor('music', 'topic_master')
cdf.controller().add_system_transition('sports', 'topic_master', '[! #UpdateNotAvailable(sports) "Sport stub."]')
cdf.controller().update_state_settings('sports', system_multi_hop=True)
cdf.controller().set_error_successor('sports', 'topic_master')
cdf.controller().add_system_transition('news', 'topic_master', '[! #UpdateNotAvailable(news) "News stub."]')
cdf.controller().update_state_settings('news', system_multi_hop=True)
cdf.controller().set_error_successor('news', 'topic_master')


cdf.add_state('suggest_topic', 'topic_master')
cdf.controller().update_state_settings('suggest_topic', memory=0)
cdf.add_state('no_topic', 'catchall')
cdf.add_state('catchall', 'catchall')
cdf.add_system_transition('topic_master', 'suggest_topic', '"."', score=0.0)
cdf.controller().update_state_settings('suggest_topic', system_multi_hop=True)

cdf.add_system_transition('suggest_topic', 'chosen_topic', '[! "We can talk about" #GetTopicSuggestions() ". Would you like to?"]')
cdf.add_user_transition('chosen_topic', 'accept_topic', '{[#EXP(yes)],[ok]}')
cdf.add_user_transition('chosen_topic', 'reject_topic', '{[#EXP(no)],[{i dont, i do not, no i dont, no i do not}]}')
cdf.add_system_transition('accept_topic', 'movies', '[! #IsTopicSuggestion(movies) "."]')
cdf.add_system_transition('accept_topic', 'music', '[! #IsTopicSuggestion(music) "."]')
cdf.add_system_transition('accept_topic', 'sports', '[! #IsTopicSuggestion(sports) "."]')
cdf.add_system_transition('accept_topic', 'news', '[! #IsTopicSuggestion(news) "."]')
cdf.controller().update_state_settings('accept_topic', memory=0)
cdf.add_system_transition('reject_topic', 'topic_master', '"Ok, of course. Let\'s find something else to talk about."')

cdf.add_system_transition('suggest_topic', 'no_topic', '"We have covered a lot of topics so far. What else would you like to talk about now?"', score=0.0)
cdf.add_system_transition('catchall', 'catchall', '"Interesting! Tell me more."')



cdf.run(debugging=True)