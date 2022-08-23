
import pytest

from emora_stdm import DialogueFlow, CompositeDialogueFlow


@pytest.fixture
def movies_df():
    df = DialogueFlow('start')
    df.global_transitions({
        '[{movie, movies}]': {
            "`I like Inception.`": 'SYSTEM:start'
        },
        '[theater]': {
            "`I went to the movies this weekend.`": 'SYSTEM:start'
        }
    })
    return df


@pytest.fixture
def sports_df():
    df = DialogueFlow('start')
    df.local_transitions({
        'state': 'start',
        'error': {
            "`Do you play sports?`": {
                'error': {
                    "`I used to play soccer.`": 'SYSTEM:start'
                }
            }
        }
    }, speaker=DialogueFlow.Speaker.USER)
    df.topic_transitions({
        '[favorite]': {
            "`Probably Barca.`": 'start'
        }
    })
    df.global_transitions({
        '[soccer]': {
            'score': 2,
            "`Messi is the best.`": 'start'
        },
        '[basketball]': {
            'score': 1,
            "`I don't really watch it...`": 'SYSTEM:start'
        }
    })
    return df


@pytest.fixture
def cdf(movies_df, sports_df):
    cdf = CompositeDialogueFlow('start', 'start', 'start')
    cdf.controller().local_transitions({
        'state': 'start',
        "`What's up?`": {
            'error': {
                "`Hmm... I'm not sure.`": 'start'
            }
        }
    })
    cdf.add_component(movies_df, 'movies')
    cdf.add_component(sports_df, 'sports')
    return cdf


def test_global_nlu(cdf):
    assert "What's up" in cdf.system_turn()
    cdf.user_turn("talk about movies")
    assert "Inception" in cdf.system_turn()
    cdf.user_turn("do you like soccer")
    assert "Messi" in cdf.system_turn()
    cdf.user_turn("Yeah.")
    assert "sports" in cdf.system_turn()
    cdf.user_turn("have you been to the theater")
    assert "movies this weekend" in cdf.system_turn()


def test_topic_nlu(cdf):
    assert "What's up" in cdf.system_turn()
    cdf.user_turn("what is your favorite team")
    assert "Barca" not in cdf.system_turn()
    cdf.user_turn("do you like soccer")
    assert "Messi" in cdf.system_turn()
    cdf.user_turn("what is your favorite team")
    assert "Barca" in cdf.system_turn()
    cdf.user_turn("talk about movies")
    assert "Inception" in cdf.system_turn()
    cdf.user_turn("what is your favorite team")
    assert "Barca" not in cdf.system_turn()


def test_global_nlu_scores(cdf):
    assert "What's up" in cdf.system_turn()
    for _ in range(10):
        cdf.user_turn("i like soccer and basketball")
        assert "Messi" in cdf.system_turn()



