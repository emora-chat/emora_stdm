
import pytest
from emora_stdm.state_transition_dialogue_manager.dialogue_flow import DialogueFlow
from emora_stdm.state_transition_dialogue_manager.natex_nlu import NatexNLU
from emora_stdm.state_transition_dialogue_manager.macros_common import GoalPursuit,GoalExit

def test_stack():
    df = DialogueFlow('root')
    transitions = {
        'state': 'root',
        '`What should I do?`':'gma_hospital',

        '#GOAL(grandma_hospital) #GATE'
        '`I cannot concentrate on a lot of things right now. '
        'My grandma is in the hospital. '
        'What should I do?`':{
            'state': 'gma_hospital',
            'score': 2.0,

            '[{[{dont,shouldnt,not},worry],calm,relax,distract,[mind,off]}]':{
                'state': 'dont_worry',

                '#GATE '
                '"Okay, I will try my best not to worry. It\'s hard because she lives by '
                'herself and won\'t let anyone help her very much, so I feel like this '
                'will just happen again."':{
                    'state': 'happen_again',

                    '[{sorry,sucks,hard}]':{
                        '"yeah, thanks."': {}
                    },
                    '[will,better]':{
                        '"I really hope you are right."': {}
                    },
                    'error': {
                        'state': 'feel_better',
                        '"I actually feel a little bit better after talking with you. Thanks for listening. "':{}
                    }
                },
                '#DEFAULT': 'feel_better'
            },
            '#IDK':{
                '"yeah, i dont know either. Its so tough."': {}
            }
        }
    }

    gma = {
        '#GOAL(why_grandma_hospital) '
        '[{[why,hospital],wrong,happened}]': {
            'state':'why_grandma_hospital',
            '"She is just so frail. I can hardly believe it. '
            'She fell off of a stool in the kitchen and broke her hip."': {
                '[dont worry]':{
                    '#GRET(grandma_hospital,dont_worry)'
                },
                'error':{
                    '#GRET': 'return'
                }
            }
        },
        '#GOAL(grandma_hospital_before) '
        '[{has,was},{she,grandma},hospital,{before,earlier,previously}]': {
            'state': 'grandma_hospital_before',
            '"No, this is the first time, thank goodness."': {
                'error':{
                    '#GRET': 'return'
                }
            }
        }
    }

    df.load_transitions(transitions)
    df.load_transitions(gma, speaker=DialogueFlow.Speaker.USER)
    df.add_global_nlu('why_grandma_hospital',
                      '#GOAL(why_grandma_hospital) [{[why,hospital],wrong,happened}]',
                      score=0.7)
    df.add_global_nlu('grandma_hospital_before',
                      '#GOAL(grandma_hospital_before) [{has,was},{she,grandma},hospital,{before,earlier,previously}]',
                      score=0.7)

    r = df.system_turn()
    assert df.vars()['__goal__'] == 'grandma_hospital'
    assert len(df.vars()['__stack__']) == 0
    assert df.state() == 'gma_hospital'

    df.user_turn("what happened")
    assert df.state() == "why_grandma_hospital"
    assert df.vars()['__goal_return_state__'] == 'None'
    assert df.vars()['__goal__'] == 'why_grandma_hospital'
    assert len(df.vars()['__stack__']) == 1
    assert df.vars()['__stack__'][0][0] == 'grandma_hospital'

    assert "fell off of a stool" in df.system_turn()
    df.user_turn("oh no", debugging=True)

    assert "What should I do" in df.system_turn(debugging=True)
    assert df.state() == 'gma_hospital'
    assert df.vars()['__goal__'] == 'grandma_hospital'
    assert len(df.vars()['__stack__']) == 0

    df.user_turn("dont worry")
    assert df.state() == 'dont_worry'
    assert "she lives by herself" in df.system_turn()

    df.user_turn("has your grandma been in the hospital before this")
    assert df.state() == 'grandma_hospital_before'
    assert df.vars()['__goal__'] == 'grandma_hospital_before'
    assert len(df.vars()['__stack__']) == 1
    assert df.vars()['__stack__'][0][0] == 'grandma_hospital'

    assert "this is the first time" in df.system_turn()

    df.user_turn("ok that is good")
    assert "feel a little bit better" in df.system_turn()
    assert df.vars()['__goal__'] == 'grandma_hospital'
    assert len(df.vars()['__stack__']) == 0