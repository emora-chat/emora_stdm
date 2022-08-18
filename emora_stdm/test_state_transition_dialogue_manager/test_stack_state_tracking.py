import pytest
from emora_stdm.state_transition_dialogue_manager.dialogue_flow import DialogueFlow
from emora_stdm.state_transition_dialogue_manager.composite_dialogue_flow import CompositeDialogueFlow

@pytest.fixture()
def df1():
    df = DialogueFlow('start', initial_speaker=DialogueFlow.Speaker.SYSTEM)
    df.load_transitions({'state': 'end'})
    df.load_transitions({
      'state': 'start',
      "`System zero.`": {
        'state': 'usr1',
        '[one]': {
          'state': 'sys1',
          "`System one.`": {
            'state': 'usr2',
            '[two]': {
              'state': 'sys3',
              "`System three.`": 'end'
            },
            'error': {
              'state': 'sys4',
              "`System four.`": 'end'
            }
          }
        },
        'error': {
          'state': 'sys2',
          "`System two.`": 'end'
        }
      }
    })
    return df

@pytest.fixture()
def df2():
    df = DialogueFlow('start', initial_speaker=DialogueFlow.Speaker.SYSTEM)
    df.load_transitions({
      'state': 'start',
      "`System a.`": {
        'state': 'usr1',
        '[one]': {
          'state': 'sys1',
          "`System c.`": {
            'state': 'usr2',
            '[two]': {
              'state': 'sys3',
              "`System d.`": 'end'
            },
            'error': 'x:sys1'
          }
        },
        'error': {
          'state': 'sys2',
          "`System b.`": 'end'
        }
      }
    })
    return df

@pytest.fixture
def cdf(df1, df2):
    cdf = CompositeDialogueFlow('start', 'start', 'usr_start')
    cdf.component('SYSTEM').load_transitions({
      'state': 'start',
      "`Cdf zero.`": {
        'state': 'usr_start',
        '[x]': 'x:start',
        'error': 'y:start'
      }
    })
    cdf.add_component(df1, 'x')
    cdf.add_component(df2, 'y')
    return cdf

def test_stack_state_tracking_1(df1):
    df1.system_turn()
    df1.user_turn('one', debugging=True)
    assert df1.vars()['__stack_return'] == 'sys1'
    df1.system_turn()
    df1.user_turn('something', debugging=True)
    assert df1.vars()['__stack_return'] == 'sys4'

def test_stack_state_tracking_2(df1):
    df1.system_turn()
    df1.user_turn('something')
    assert df1.vars()['__stack_return'] == 'sys2'

def test_stack_state_tracking_cdf(cdf):
    cdf.system_turn()
    cdf.user_turn('')
    cdf.system_turn()
    cdf.user_turn('one')
    cdf.system_turn()
    cdf.user_turn('')
    assert cdf.controller().vars()['__stack_return'] == ('x', 'sys1')
