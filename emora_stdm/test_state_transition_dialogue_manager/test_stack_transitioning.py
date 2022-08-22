import pytest

from emora_stdm import DialogueFlow, CompositeDialogueFlow


@pytest.fixture
def activity():
    df = DialogueFlow('start', initial_speaker=DialogueFlow.Speaker.SYSTEM)
    df.local_transitions({
        'state': 'start',
        "`What did you do this weekend?`": {
            '[nothing]': {
                'state': 'activity_return',
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
    }, default_score=2)
    df.local_transitions({
        'state': 'start',
        "`I went to the movies.`": {
            '[who, with]': {
                "`I went with my friend.`": 'end'
            },
            'error': {
                'state': 'theater_return',
                "`I haven't been to the theater in a while. It was fun.`": 'end'
            }
        }
    })
    df.local_transitions({
        'state': 'end',
        "#RET": 'SYSTEM:start'
    })
    return df


@pytest.fixture
def movie():
    df = DialogueFlow('start', initial_speaker=DialogueFlow.Speaker.SYSTEM)
    df.global_transitions({
        '#JMP [your, favorite, movie]': 'start'
    }, default_score=2)
    df.local_transitions({
        'state': 'start',
        "`My favorite movie is Inception.`": {
            '[why]': {
                "`I like the ending.`": 'end'
            },
            'error': {
                'state': 'movie_end',
                "`Yeah. It's a good Christopher Nolan film.`": 'end'
            }
        }
    })
    df.local_transitions({
        'state': 'end',
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


def test_stack_transitioning(cdf):
    assert 'What did you do' in cdf.system_turn()
    cdf.user_turn('nothing what did you do this weekend')
    assert 'I went to the movies' in cdf.system_turn()
    cdf.user_turn('what is your favorite movie')
    assert 'Inception' in cdf.system_turn()
    cdf.user_turn('i like that one too')
    system_turn = cdf.system_turn()
    assert 'Nolan' in system_turn
    assert 'It was fun.' in system_turn
    assert 'nice to just relax' in system_turn


@pytest.fixture
def theater_explicit_jump_point():
    df = DialogueFlow('start', initial_speaker=DialogueFlow.Speaker.SYSTEM)
    df.global_transitions({
        '#JMP [you, do, weekend]': 'start'
    }, default_score=2)
    df.local_transitions({
        'state': 'start',
        "`I went to the movies.`": {
            '[who, with]': {
                "`I went with my friend.`": 'end'
            },
            'error': {
                'state': 'theater_return',
                "`I haven't been to the theater in a while. It was fun.`": 'end'
            },
            '#RPT': {
                '`Anyways...`': 'theater_return'
            }
        }
    })
    df.local_transitions({
        'state': 'end',
        "#RET": 'SYSTEM:start'
    })
    return df


@pytest.fixture
def cdf_explicit_jump_point(activity, theater_explicit_jump_point, movie):
    cdf = CompositeDialogueFlow('start', 'start', 'end')
    cdf.component('SYSTEM').local_transitions({
        'state': 'start',
        "`Hi I'm Emora.`": 'activity:start'
    })
    cdf.add_component(activity, 'activity')
    cdf.add_component(theater_explicit_jump_point, 'theater')
    cdf.add_component(movie, 'movie')
    return cdf


def test_explicit_jump_point(cdf_explicit_jump_point):
    cdf = cdf_explicit_jump_point
    assert 'What did you do' in cdf.system_turn()
    cdf.user_turn('nothing what did you do this weekend')
    assert 'I went to the movies' in cdf.system_turn()
    cdf.user_turn('what is your favorite movie')
    assert 'Inception' in cdf.system_turn()
    cdf.user_turn('i like that one too')
    system_turn = cdf.system_turn()
    assert 'Nolan' in system_turn
    assert 'Anyways... I have' in system_turn
    assert 'nice to just relax' in system_turn






