from emora_stdm.old_StateTransitionDialogueManager.dialogue_flow import DialogueTransition, DialogueFlow
from emora_stdm.old_StateTransitionDialogueManager.knowledge_base import KnowledgeBase

def test_nlg_score_update():

    df = DialogueFlow('start')
    df._kb = KnowledgeBase()
    df.add_states(list('xy12345678')+['start'])

    df.add_transition('start', '1', None, {'start to 1'})
    df.add_transition('start', '2', None, {'start to 2'})
    df.add_transition('start', '3', None, {'start to 3'})

    utterance = df.system_transition()

    if utterance == 'start to 1':
        assert df.get_transition('start', '1').get_nlg_score() == 0
        assert df.get_transition('start', '2').get_nlg_score() == 11
        assert df.get_transition('start', '3').get_nlg_score() == 11
    elif utterance == 'start to 2':
        assert df.get_transition('start', '1').get_nlg_score() == 11
        assert df.get_transition('start', '2').get_nlg_score() == 0
        assert df.get_transition('start', '3').get_nlg_score() == 11
    elif utterance == 'start to 3':
        assert df.get_transition('start', '1').get_nlg_score() == 11
        assert df.get_transition('start', '2').get_nlg_score() == 11
        assert df.get_transition('start', '3').get_nlg_score() == 0
    else:
        assert False

def test_nlg_score_save_load():

    df = DialogueFlow('start')
    df._kb = KnowledgeBase()
    df.add_states(list('xy12345678')+['start'])

    df.add_transition('start', '1', None, {'start to 1'})
    df.add_transition('start', '2', None, {'start to 2'})
    df.add_transition('start', '3', None, {'start to 3'})

    utterance = df.system_transition()

    if utterance == 'start to 1':
        assert df.get_transition('start', '1').get_nlg_score() == 0
        assert df.get_transition('start', '2').get_nlg_score() == 11
        assert df.get_transition('start', '3').get_nlg_score() == 11
    elif utterance == 'start to 2':
        assert df.get_transition('start', '1').get_nlg_score() == 11
        assert df.get_transition('start', '2').get_nlg_score() == 0
        assert df.get_transition('start', '3').get_nlg_score() == 11
    elif utterance == 'start to 3':
        assert df.get_transition('start', '1').get_nlg_score() == 11
        assert df.get_transition('start', '2').get_nlg_score() == 11
        assert df.get_transition('start', '3').get_nlg_score() == 0
    else:
        assert False

    scores = df.nlg_transition_scores_to_json_string()

    df2 = DialogueFlow('start')
    df2._kb = KnowledgeBase()
    df2.add_states(list('xy12345678') + ['start'])

    df2.add_transition('start', '1', None, {'start to 1'})
    df2.add_transition('start', '2', None, {'start to 2'})
    df2.add_transition('start', '3', None, {'start to 3'})

    df2.load_nlg_transition_scores(scores)

    if utterance == 'start to 1':
        assert df2.get_transition('start', '1').get_nlg_score() == 0
        assert df2.get_transition('start', '2').get_nlg_score() == 11
        assert df2.get_transition('start', '3').get_nlg_score() == 11
    elif utterance == 'start to 2':
        assert df2.get_transition('start', '1').get_nlg_score() == 11
        assert df2.get_transition('start', '2').get_nlg_score() == 0
        assert df2.get_transition('start', '3').get_nlg_score() == 11
    elif utterance == 'start to 3':
        assert df2.get_transition('start', '1').get_nlg_score() == 11
        assert df2.get_transition('start', '2').get_nlg_score() == 11
        assert df2.get_transition('start', '3').get_nlg_score() == 0

    utterance2 = df2.system_transition()

    assert utterance2 != utterance
    if utterance == 'start to 1' and utterance2 == 'start to 2':
        assert df2.get_transition('start', '1').get_nlg_score() == 1
        assert df2.get_transition('start', '2').get_nlg_score() == 0
        assert df2.get_transition('start', '3').get_nlg_score() == 12
    elif utterance == 'start to 1' and utterance2 == 'start to 3':
        assert df2.get_transition('start', '1').get_nlg_score() == 1
        assert df2.get_transition('start', '2').get_nlg_score() == 12
        assert df2.get_transition('start', '3').get_nlg_score() == 0
    elif utterance == 'start to 2' and utterance2 == 'start to 1':
        assert df2.get_transition('start', '1').get_nlg_score() == 0
        assert df2.get_transition('start', '2').get_nlg_score() == 1
        assert df2.get_transition('start', '3').get_nlg_score() == 12
    elif utterance == 'start to 2' and utterance2 == 'start to 3':
        assert df2.get_transition('start', '1').get_nlg_score() == 12
        assert df2.get_transition('start', '2').get_nlg_score() == 1
        assert df2.get_transition('start', '3').get_nlg_score() == 0
    elif utterance == 'start to 3' and utterance2 == 'start to 1':
        assert df2.get_transition('start', '1').get_nlg_score() == 0
        assert df2.get_transition('start', '2').get_nlg_score() == 12
        assert df2.get_transition('start', '3').get_nlg_score() == 1
    elif utterance == 'start to 3' and utterance2 == 'start to 2':
        assert df2.get_transition('start', '1').get_nlg_score() == 12
        assert df2.get_transition('start', '2').get_nlg_score() == 0
        assert df2.get_transition('start', '3').get_nlg_score() == 1
    else:
        assert False