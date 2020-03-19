
import pytest
from emora_stdm import DialogueFlow
from emora_stdm.state_transition_dialogue_manager.composite_dialogue_flow import CompositeDialogueFlow


if __name__ == '__main__':
    df1 = DialogueFlow('A', initial_speaker=DialogueFlow.Speaker.USER)
    df1.add_state('A', 6)
    df1.add_state(6)
    df1.add_state('C', 'D')
    df1.add_state('D')
    df1.add_user_transition('A', 'D', '$fruit=apple dog')
    df1.add_system_transition(6, 'C', 'banana catfish')
    df1.add_system_transition('D', 'A', 'dog apple')
    #df1.add_system_transition(6, ('movie', 'Y'), 'movie')
    #df1.run(debugging=True)

    df2 = DialogueFlow('A', initial_speaker=DialogueFlow.Speaker.USER)
    df2.add_state('A', 6)
    df2.add_state(6)
    df2.add_state('C', 'D')
    df2.add_state('D')
    df2.add_user_transition('A', 'D', '$state=alaska down')
    df2.add_system_transition(6, 'C', 'bark call')
    df2.add_system_transition('D', 'A', 'down alaska')
    #df2.run(debugging=True)

    df2.add_state(('SYSTEM', 'topic_err'), global_nlu='back')
    df2.add_state(('one', 6), global_nlu='dog')

    cdf = CompositeDialogueFlow('start', initial_speaker=DialogueFlow.Speaker.USER,
                                system_error_state='topic_err', user_error_state='topic_err')
    cdf.add_component(df1, 'one')
    cdf.add_component(df2, 'two')
    cdf.add_state('start', 'greet')
    cdf.add_state('greet')
    cdf.add_state('topic', 'topic_err')
    cdf.add_state('topic_err')
    cdf.add_system_transition('topic_err', 'topic', 'what do you want to discuss')
    cdf.add_system_transition('greet', 'topic', 'hello')
    cdf.add_user_transition('topic', ('one', 6), '$animal={catfish, dog}')
    cdf.add_user_transition('topic', ('two', 6), '$item={alaska, bark, down}')
    cdf.add_user_transition(('one', 'A'), ('SYSTEM', 'topic_err'), 'back')

    cdf.precache_transitions(1)

    cdf.run(debugging=False)