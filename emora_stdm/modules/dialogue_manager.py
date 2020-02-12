
from emora_stdm import DialogueFlow, Macro
from emora_stdm.state_transition_dialogue_manager.composite_dialogue_flow import CompositeDialogueFlow
from modules.opening import component as opening
from modules.hobby import df as hobby
from modules.hobby import State as hobby_states
from modules.pets import df as pet
from modules.pets import State as pet_states
from modules.family import df as family
from modules.stop_conversation import df as stop

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
            vars['dm-not_available'] = []
        vars['dm-not_available'].append(args[0])

macros = {"Available":Available(), "NotAvailable":NotAvailable(), "UpdateNotAvailable":UpdateNotAvailable()}

cdf = CompositeDialogueFlow('start', initial_speaker=DialogueFlow.Speaker.USER, macros=macros)
cdf.add_component(opening, 'opening')
cdf.add_user_transition('start', ('opening', 'prestart'), '/.*/')
cdf.controller().update_state_settings(('opening', 'prestart'), user_multi_hop=True)

cdf.add_state('topic_master', 'topic_master')
opening.add_system_transition('transition_out', ('SYSTEM', 'topic_master'), '"."')

cdf.add_component(hobby, 'hobby')
cdf.add_system_transition('topic_master', ('hobby', hobby_states.INTRO_READING), '[! #Available(hobby) #UpdateNotAvailable(hobby) "."]')
cdf.controller().update_state_settings(('hobby', hobby_states.INTRO_READING), system_multi_hop=True)
hobby.add_system_transition(hobby_states.TRANSITION_OUT, ('SYSTEM', 'topic_master'), '"."')

cdf.add_component(pet, 'pet')
cdf.add_system_transition('topic_master', ('pet', pet_states.PETS_Y), '[! #Available(pet) #UpdateNotAvailable(pet) "."]')
cdf.controller().update_state_settings(('pet', pet_states.PETS_Y), system_multi_hop=True)
pet.add_system_transition(pet_states.END, ('SYSTEM', 'topic_master'), '"I have really liked learning about your experiences with pets."')

# cdf.add_component(family, 'family')
# cdf.add_system_transition('topic_master', ('family', hobby_states.INTRO_READING), '"."')
# cdf.controller().update_state_settings(('family', hobby_states.INTRO_READING), system_multi_hop=True)
# family.add_system_transition(hobby_states.TRANSITION_OUT, ('SYSTEM', 'topic_master'), '"."')
# family.update_state_settings(('SYSTEM', 'topic_master'), system_multi_hop=True)


########################
# External components
########################

cdf.controller().add_state('movies', global_nlu='{movie,movies,film,films,tv,shows,television}')
cdf.controller().add_state('music', global_nlu='{music,song,songs,melody,melodies,album,albums,concert,concerts}')
cdf.controller().add_state('sports', global_nlu='{sport,sports,athletics,basketball,football,hockey,golf,tennis}')
cdf.controller().add_state('news', global_nlu='{news}')
cdf.controller().update_state_settings(('pet', pet_states.PETS_Y), global_nlu='{pet,pets,animals,animal,cat,cats,dog,dogs}')
cdf.controller().update_state_settings(('hobby', hobby_states.INTRO_READING), global_nlu='{hobby,hobbies,activity,activities,fun things,things to do,pasttimes}')

cdf.controller().add_system_transition('movies', 'movies', '"Movie stub."')
cdf.controller().set_error_successor('movies', 'topic_master')
cdf.controller().add_system_transition('music', 'music', '"Music stub."')
cdf.controller().set_error_successor('music', 'topic_master')
cdf.controller().add_system_transition('sports', 'sports', '"Sport stub."')
cdf.controller().set_error_successor('sports', 'topic_master')
cdf.controller().add_system_transition('news', 'news', '"News stub."')
cdf.controller().set_error_successor('news', 'topic_master')

cdf.add_system_transition('topic_master', 'topic_master', '"We are talking about something new."', score=0.0)
cdf.controller().set_error_successor('topic_master', 'topic_master')
cdf.controller().update_state_settings('topic_master', memory=0)
#cdf.add_system_transition('error_state', 'error_state', '"Ran out of topics."')


cdf.run(debugging=False)