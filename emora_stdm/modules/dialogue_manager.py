
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
cdf.controller().update_state_settings('topic_master', system_multi_hop=True)
opening.add_system_transition('transition_out', ('SYSTEM', 'topic_master'), '"."')
opening.update_state_settings(('SYSTEM', 'topic_master'), system_multi_hop=True)

cdf.add_component(hobby, 'hobby')
cdf.add_system_transition('topic_master', ('hobby', hobby_states.INTRO_READING), '[! #Available(hobby) #UpdateNotAvailable(hobby) "."]')
cdf.controller().update_state_settings(('hobby', hobby_states.INTRO_READING), system_multi_hop=True)
hobby.add_system_transition(hobby_states.TRANSITION_OUT, ('SYSTEM', 'topic_master'), '"."')
hobby.update_state_settings(('SYSTEM', 'topic_master'), system_multi_hop=True)

cdf.add_component(pet, 'pet')
cdf.add_system_transition('topic_master', ('pet', pet_states.PETS_Y), '[! #Available(pet) #UpdateNotAvailable(pet) "."]')
cdf.controller().update_state_settings(('pet', pet_states.PETS_Y), system_multi_hop=True)
pet.add_system_transition(pet_states.END, ('SYSTEM', 'topic_master'), '"."')
pet.update_state_settings(('SYSTEM', 'topic_master'), system_multi_hop=True)

# cdf.add_component(family, 'family')
# cdf.add_system_transition('topic_master', ('family', hobby_states.INTRO_READING), '"."')
# cdf.controller().update_state_settings(('family', hobby_states.INTRO_READING), system_multi_hop=True)
# family.add_system_transition(hobby_states.TRANSITION_OUT, ('SYSTEM', 'topic_master'), '"."')
# family.update_state_settings(('SYSTEM', 'topic_master'), system_multi_hop=True)

cdf.add_system_transition('topic_master', 'error_state', '"We are talking about something new."', score=0.0)
cdf.controller().set_error_successor('error_state', 'error_state')
cdf.add_system_transition('error_state', 'error_state', '"Ran out of topics."')


cdf.run(debugging=True)