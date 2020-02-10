
import pytest
from emora_stdm import DialogueFlow
from emora_stdm.state_transition_dialogue_manager.composite_dialogue_flow import CompositeDialogueFlow


if __name__ == '__main__':
    df1 = DialogueFlow('A', initial_speaker=DialogueFlow.Speaker.USER)
    df1.add_state('A', 'B')
    df1.add_state('B')
    df1.add_state('C', 'D')
    df1.add_state('D')
    df1.add_user_transition('A', 'D', 'apple dog')
    df1.add_system_transition('B', 'C', 'banana catfish')
    df1.add_system_transition('D', 'A', 'dog apple')
    df1.add_user_transition('A', ('SYSTEM', 'topic_err'), 'back')
    #df1.add_system_transition('B', ('movie', 'Y'), 'movie')
    #df1.run(debugging=True)

    df2 = DialogueFlow('A', initial_speaker=DialogueFlow.Speaker.USER)
    df2.add_state('A', 'B')
    df2.add_state('B')
    df2.add_state('C', 'D')
    df2.add_state('D')
    df2.add_user_transition('A', 'D', 'alaska down')
    df2.add_system_transition('B', 'C', 'bark call')
    df2.add_system_transition('D', 'A', 'down alaska')
    df2.add_user_transition('A', ('SYSTEM', 'topic_err'), 'back')
    #df2.run(debugging=True)

    cdf = CompositeDialogueFlow('start', initial_speaker=DialogueFlow.Speaker.USER)
    cdf.add_component(df1, 'one')
    cdf.add_component(df2, 'two')
    cdf.add_state('start', 'greet')
    cdf.add_state('greet')
    cdf.add_state('topic', 'topic_err')
    cdf.add_state('topic_err')
    cdf.add_system_transition('topic_err', 'topic', 'what do you want to discuss')
    cdf.add_system_transition('greet', 'topic', 'hello')
    cdf.add_user_transition('topic', ('one', 'B'), '{catfish, dog}')
    cdf.add_user_transition('topic', ('two', 'B'), '{alaska, bark, down}')

    cdf.run(debugging=True)