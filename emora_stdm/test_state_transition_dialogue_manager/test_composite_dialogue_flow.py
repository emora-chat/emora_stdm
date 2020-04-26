

import pytest
from emora_stdm import DialogueFlow
from emora_stdm.state_transition_dialogue_manager.composite_dialogue_flow import CompositeDialogueFlow


def test_composite_df_working():
    df1 = DialogueFlow('A', initial_speaker=DialogueFlow.Speaker.USER)
    df1.add_state('A', 'X')
    df1.add_state('X')
    df1.add_state('C', 'D')
    df1.add_state('D')
    df1.add_user_transition('A', 'D', '$fruit=apple dog')
    df1.add_system_transition('X', 'C', 'banana catfish')
    df1.add_system_transition('D', 'A', 'dog apple')
    #df1.add_system_transition('X', ('movie', 'Y'), 'movie')
    #df1.run(debugging=True)

    df2 = DialogueFlow('A', initial_speaker=DialogueFlow.Speaker.USER)
    df2.add_state('A', 'X')
    df2.add_state('X')
    df2.add_state('C', 'D')
    df2.add_state('D')
    df2.add_user_transition('A', 'D', '$state=alaska down')
    df2.add_system_transition('X', 'C', 'bark call')
    df2.add_system_transition('D', 'A', 'down alaska')
    #df2.run(debugging=True)

    df2.add_state(('SYSTEM', 'topic_err'), global_nlu='back')
    df2.add_state(('one', 'X'), global_nlu='dog')

    cdf = CompositeDialogueFlow('start', 'topic_err', 'topic', initial_speaker=DialogueFlow.Speaker.USER)
    cdf.add_component(df1, 'one')
    cdf.add_component(df2, 'two')
    cdf.add_state('start', 'greet')
    cdf.add_state('greet')
    cdf.add_state('topic', 'topic_err')
    cdf.add_state('topic_err')
    cdf.add_system_transition('topic_err', 'topic', 'what do you want to discuss')
    cdf.add_system_transition('greet', 'topic', 'hello')
    cdf.add_user_transition('topic', ('one', 'X'), '$animal={catfish, dog}')
    cdf.add_user_transition('topic', ('two', 'X'), '$item={alaska, bark, down}')
    cdf.add_user_transition(('one', 'A'), ('SYSTEM', 'topic_err'), 'back')

    cdf.user_turn('hello')
    assert cdf.system_turn() == 'hello'
    cdf.user_turn('bark')
    assert cdf.controller_name() == 'two'
    assert cdf.system_turn() == 'bark call'
    cdf.user_turn('back')
    assert cdf.controller_name() == 'SYSTEM'

def test_composite_df_with_error_in_component():
    df1 = DialogueFlow('A', initial_speaker=DialogueFlow.Speaker.USER)
    df1.add_state('A', 'X')
    df1.add_state('X')
    df1.add_state('C', 'D')
    df1.add_state('D')
    df1.add_user_transition('A', 'D', '$fruit=apple dog')
    df1.add_system_transition('X', 'C', 'banana catfish')
    df1.add_system_transition('D', 'A', 'dog apple')
    #df1.add_system_transition('X', ('movie', 'Y'), 'movie')
    #df1.run(debugging=True)

    df2 = DialogueFlow('A', initial_speaker=DialogueFlow.Speaker.USER)
    df2.add_state('A', 'X')
    df2.add_state('X')
    df2.add_state('C', 'D')
    df2.add_state('D')
    df2.add_user_transition('A', 'D', '$state=alaska down')

    df2.add_state(('SYSTEM', 'topic_err'), global_nlu='back')
    df2.add_state(('one', 'X'), global_nlu='dog')

    cdf = CompositeDialogueFlow('start', 'topic_err', 'topic', initial_speaker=DialogueFlow.Speaker.USER)
    cdf.add_component(df1, 'one')
    cdf.add_component(df2, 'two')
    cdf.add_state('start', 'greet')
    cdf.add_state('greet')
    cdf.add_state('topic', 'topic_err')
    cdf.add_state('topic_err')
    cdf.add_system_transition('topic_err', 'topic', 'what do you want to discuss')
    cdf.add_system_transition('greet', 'topic', 'hello')
    cdf.add_user_transition('topic', ('one', 'X'), '$animal={catfish, dog}')
    cdf.add_user_transition('topic', ('two', 'X'), '$item={alaska, bark, down}')
    cdf.add_user_transition(('one', 'A'), ('SYSTEM', 'topic_err'), 'back')

    cdf.user_turn('hello')
    assert cdf.system_turn() == 'hello'
    cdf.user_turn('bark')
    assert cdf.controller_name() == 'two'
    assert cdf.system_turn().strip() == 'what do you want to discuss'
    cdf.user_turn('catfish')
    assert cdf.controller_name() == 'one'

def test_composite_df_with_error_in_composite():
    #NOT A VALID TEST: MODIFY TO MAKE ERROR IN COMPOSITE DIALOGUE FLOW

    df1 = DialogueFlow('A', initial_speaker=DialogueFlow.Speaker.USER)
    df1.add_state('A', 'X')
    df1.add_state('X')
    df1.add_state('C', 'D')
    df1.add_state('D')
    df1.add_user_transition('A', 'D', '$fruit=apple dog')
    df1.add_system_transition('X', 'C', 'banana catfish')
    df1.add_system_transition('D', 'A', 'dog apple')
    #df1.add_system_transition('X', ('movie', 'Y'), 'movie')
    #df1.run(debugging=True)

    df2 = DialogueFlow('A', initial_speaker=DialogueFlow.Speaker.USER)
    df2.add_state('A', 'X')
    df2.add_state('X')
    df2.add_state('C', 'D')
    df2.add_state('D')
    df2.add_user_transition('A', 'D', '$state=alaska down')

    df2.add_state(('SYSTEM', 'topic_err'), global_nlu='back')
    df2.add_state(('one', 'X'), global_nlu='dog')

    cdf = CompositeDialogueFlow('start', 'topic_err', 'topic', initial_speaker=DialogueFlow.Speaker.USER)
    cdf.add_component(df1, 'one')
    cdf.add_component(df2, 'two')
    cdf.add_state('start', 'greet')
    cdf.add_state('greet')
    cdf.add_state('topic', 'topic_err')
    cdf.add_state('topic_err')
    cdf.add_system_transition('topic_err', 'topic', 'what do you want to discuss')
    cdf.add_system_transition('greet', 'topic', 'hello')
    cdf.add_user_transition('topic', ('one', 'X'), '$animal={catfish, dog}')
    cdf.add_user_transition('topic', ('two', 'X'), '$item={alaska, bark, down}')
    cdf.add_user_transition(('one', 'A'), ('SYSTEM', 'topic_err'), 'back')

    cdf.user_turn('hello')
    assert cdf.system_turn() == 'hello'
    cdf.user_turn('bark')
    assert cdf.controller_name() == 'two'
    assert cdf.system_turn().strip() == 'what do you want to discuss'
    cdf.user_turn('catfish')
    assert cdf.controller_name() == 'one'

def test_serialization():
    df1 = DialogueFlow('A', initial_speaker=DialogueFlow.Speaker.USER)
    df1.add_state('A', 'X')
    df1.add_state('X')
    df1.add_state('C', 'D')
    df1.add_state('D')
    df1.add_user_transition('A', 'D', '$fruit=apple dog')
    df1.add_system_transition('X', 'C', 'banana catfish')
    df1.add_system_transition('D', 'A', 'dog apple')
    #df1.add_system_transition('X', ('movie', 'Y'), 'movie')
    #df1.run(debugging=True)

    df2 = DialogueFlow('A', initial_speaker=DialogueFlow.Speaker.USER)
    df2.add_state('A', 'X')
    df2.add_state('X')
    df2.add_state('C', 'D')
    df2.add_state('D')
    df2.add_user_transition('A', 'D', '$state=alaska down')

    df2.add_state(('SYSTEM', 'topic_err'), global_nlu='back')
    df2.add_state(('one', 'X'), global_nlu='dog')

    cdf = CompositeDialogueFlow('start', 'topic_err', 'topic', initial_speaker=DialogueFlow.Speaker.USER)
    cdf.add_component(df1, 'one')
    cdf.add_component(df2, 'two')
    cdf.add_state('start', 'greet')
    cdf.add_state('greet')
    cdf.add_state('topic', 'topic_err')
    cdf.add_state('topic_err')
    cdf.add_system_transition('topic_err', 'topic', 'what do you want to discuss')
    cdf.add_system_transition('greet', 'topic', 'hello')
    cdf.add_user_transition('topic', ('one', 'X'), '$animal={catfish, dog}')
    cdf.add_user_transition('topic', ('two', 'X'), '$item={alaska, bark, down}')
    cdf.add_user_transition(('one', 'A'), ('SYSTEM', 'topic_err'), 'back')

    cdf.new_turn()
    cdf.user_turn('hello')
    assert cdf.system_turn() == 'hello'
    s = cdf.serialize()

    cdf.new_turn()
    cdf.deserialize(s)
    cdf.user_turn('bark')
    assert cdf.controller_name() == 'two'
    assert cdf.system_turn().strip() == 'what do you want to discuss'
    s = cdf.serialize()

    cdf.new_turn()
    cdf.deserialize(s)
    cdf.user_turn('catfish')
    assert cdf.controller_name() == 'one'
