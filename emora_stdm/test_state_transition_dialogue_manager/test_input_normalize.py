
from emora_stdm import DialogueFlow

def test_input_normalize():
    df = DialogueFlow(
        'start',
        initial_speaker=DialogueFlow.Speaker.USER,
        end_state='end'
    )
    df.load_transitions({
        'state': 'start',
        '[test]': {
            "`Success.`": 'end'
        },
        'error': {
            "`Fail.`": 'end'
        }
    })
    df.user_turn("This is a tesT.")
    assert df.system_turn() == "Success."