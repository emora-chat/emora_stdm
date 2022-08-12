import pytest

from emora_stdm import DialogueFlow, CompositeDialogueFlow


@pytest.fixture
def activity():
    df = DialogueFlow('start', initial_speaker=DialogueFlow.Speaker.SYSTEM)
    df.local_transitions({
        'state': 'start',
        "`What did you do this weekend?`": {
            '[nothing]': {
                "`Sometimes it's nice to just relax.`": 'end'
            },
            'error': {
                "`Sounds like you had a fun weekend.`": 'end'
            }
        }
    })
    return df


@pytest.fixture
def theater():
    df = DialogueFlow('start', initial_speaker=DialogueFlow.Speaker.SYSTEM)
    df.global_transitions({
        '#JMP [you, do, weekend]': 'start'
    })
    df.local_transitions({
        'state': 'start',
        "`I went to the movies.`": {
            '[who, with]': {
                "`I went with my friend.`": 'end'
            },
            'error': {
                "`I haven't been to the theater in a while. It was fun.`": 'end'
            }
        }
    })
    df.local_transitions({
        'state': 'end',
        'speaker': 'system',
        "#RET": 'SYSTEM:start'
    })
    return df


@pytest.fixture
def movie():
    df = DialogueFlow('start', initial_speaker=DialogueFlow.Speaker.SYSTEM)
    df.global_transitions({
        '#JMP [your, favorite, movie]': 'start'
    })
    df.local_transitions({
        'state': 'start',
        "`My favorite movie is Inception.`": {
            '[why]': {
                "`I like the ending.`": 'end'
            },
            'error': {
                "`Yeah. It's a good Christopher Nolan film.`": 'end'
            }
        }
    })
    df.local_transitions({
        'state': 'end',
        'speaker': 'system',
        "#RET": 'SYSTEM:start'
    })
    return df


@pytest.fixture
def cdf(activity, theater, movie):
    cdf = CompositeDialogueFlow('start', 'start', 'end')
    cdf.component('SYSTEM').local_transitions({
        'state': 'start',
        "`Hi I'm Emora.`": 'activity:start'
    })
    cdf.add_component(activity, 'activity')
    cdf.add_component(theater, 'theater')
    cdf.add_component(movie, 'movie')
    return cdf

