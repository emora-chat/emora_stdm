

from emora_stdm import DialogueFlow
import emora_stdm.state_transition_dialogue_manager.natex_common as natexes

class ChatFlow(DialogueFlow):

    def __init__(self, *json_files):
        DialogueFlow.__init__(self, 'sr', initial_speaker=DialogueFlow.Speaker.SYSTEM)
        self.add_state('sr', system_multi_hop=True)
        #self.add_state('shortcut', system_multi_hop=True)
        self.add_state('ur', 'ur_error', user_multi_hop=True)
        self.add_state('ur_error', 'ur_error_statement', user_multi_hop=True)
        self.add_user_transition('ur_error', 'ur_error_question', natexes.question)
        self.add_state('ur_error_statement')
        self.add_system_transition('ur_error_statement', 'sr', '{"Yeah." "For sure." "Yep." "Right." "Sure." "Gotcha."}', score=1.0)
        #self.add_system_transition('ur_error_statement', 'shortcut', '#TOKLIMIT(2)', score=2.0)
        #self.add_system_transition('shortcut', 'sr', '""')
        self.add_system_transition('ur_error_question', 'sr',
            '{"I\'m not sure about that." "That\'s a tough one." "I\'m not sure actually." "Huh, I don\'t know."}')
        self.add_state('dinit', system_multi_hop=True)
        self.add_system_transition('dinit', 'sr', '')
        for json_file in json_files:
            DialogueFlow.knowledge_base(self).load_json_file(json_file)
