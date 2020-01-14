from src.StateTransitionDialogueManager.dialogue_flow import DialogueFlow
from src.StateTransitionDialogueManager.dialogue_transition import DialogueTransition as dt
from datetime import datetime
import pytz
import random
from collections import defaultdict

component = DialogueFlow('prestart')
with open('modules/opening_database.json', 'r') as json_file:
    component.knowledge_base().load_json(json_file.read())

standard_opening = "Hi this is an Alexa Prize Socialbot."
inquire_feeling = "How are you today?"
time_acknowledgement = "$time_of_day_stat . "
transition_out = "What would you like to talk about today?"


def check_launch_request(arg_dict):
    if arg_dict:
        if arg_dict["request_type"] == "LaunchRequest":
            return dt.HIGHSCORE, {}
    return 0, {}

def update_time_of_day_ack_variable(curr_hour = None):
    if curr_hour is None:
        curr_hour = datetime.now(pytz.timezone('US/Eastern')).hour
    morning = ['its pretty early in the morning for me', 'its pretty early where I am']
    midday = ['its the middle of the day for me', 'its the middle of my day here']
    afternoon = ['im reaching the end of the afternoon here', 'its been a long day for me']
    evening = ['its getting dark where I live', 'its getting pretty late for me here']
    if 0 <= curr_hour < 9:
        return random.choice(morning)
    elif 9 <= curr_hour < 14:
        return random.choice(midday)
    elif 14 <= curr_hour < 19:
        return random.choice(afternoon)
    else:
        return random.choice(evening)

def check_new(arg_dict):
    if arg_dict:
        if "prev_conv_date" not in arg_dict or arg_dict["prev_conv_date"] is None:
            var_update = {'time_of_day_stat': update_time_of_day_ack_variable()}
            return dt.HIGHSCORE, var_update
    return 0, {}

def check_infreq(arg_dict):
    if arg_dict:
        if "prev_conv_date" in arg_dict and arg_dict["prev_conv_date"] is not None:
            old_datetime = datetime.strptime(arg_dict["prev_conv_date"], '%Y-%m-%d %H:%M:%S.%f')
            curr_time = datetime.now(pytz.timezone('US/Eastern'))
            delta = curr_time - old_datetime
            if delta.days >= 7:
                var_update = {'time_of_day_stat': update_time_of_day_ack_variable(curr_time.hour)}
                return dt.HIGHSCORE, var_update
    return 0, {}

def check_freq(arg_dict):
    if arg_dict:
        if "prev_conv_date" in arg_dict and arg_dict["prev_conv_date"] is not None:
            old_datetime = datetime.strptime(arg_dict["prev_conv_date"], '%Y-%m-%d %H:%M:%S.%f')
            curr_time = datetime.now(pytz.timezone('US/Eastern'))
            delta = curr_time - old_datetime
            if delta.days < 7:
                var_update = {'time_of_day_stat': update_time_of_day_ack_variable(curr_time.hour)}
                return dt.HIGHSCORE, var_update
    return 0, {}

def is_new_user(utterance, arg_dict, score):
    score, vars = check_launch_request(arg_dict)
    if score == dt.HIGHSCORE:
        score, vars = check_new(arg_dict)
        if score == dt.HIGHSCORE:
            return dt.HIGHSCORE, vars
    return 0, {}

def is_infreq_user(utterance, arg_dict, score):
    score, vars = check_launch_request(arg_dict)
    if score == dt.HIGHSCORE:
        score, vars = check_infreq(arg_dict)
        if score == dt.HIGHSCORE:
            return dt.HIGHSCORE, vars
    return 0, {}

def is_freq_user(utterance, arg_dict, score):
    score, vars = check_launch_request(arg_dict)
    if score == dt.HIGHSCORE:
        score, vars = check_freq(arg_dict)
        if score == dt.HIGHSCORE:
            return dt.HIGHSCORE, vars
    return 0, {}

def is_positive_sentiment(utterance, arg_dict, score):
    if score > 0:
        return score, {}
    if arg_dict["pos_sentiment"]:
        return dt.HIGHSCORE, {}
    else:
        return 0, {}

def is_negative_sentiment(utterance, arg_dict, score):
    if score > 0:
        return score, {}
    if not arg_dict["pos_sentiment"]:
        return dt.HIGHSCORE, {}
    else:
        return 0, {}

def how_are_you_state_selection(df, utterance, graph_arcs):
    best_score, next_state, vars_update = None, None, None
    matches, vars_dict = defaultdict(dict), defaultdict(dict)
    for source, target, transition in graph_arcs:
        score, vars = transition.eval_user_transition(utterance, df.vars())
        if score > 0:
            matches[source][target] = score
            vars_dict[source][target] = vars
    if len(matches) > 0:
        best_score = max([score for source in matches for target, score in matches[source].items()])
        for source in matches:
            for target, score in matches[source].items():
                if score == best_score and ('neutral' in target or 'decline' in target):
                    return best_score, target, vars_dict[source][target]
                elif score == best_score:
                    best_score, next_state, vars_update = score, target, vars_dict[source][target]
    return best_score, next_state, vars_update

states = ['prestart', 'start_new', 'start_infreq', 'start_freq', 'receive_name',
          'missed_name', 'acknowledge_name', 'got_name', 'how_are_you',
          'feeling_pos', 'feeling_neg', 'feeling_neutral', 'unrecognized_emotion',
          'decline_share', 'end', 'acknowledge_pos', 'acknowledge_neg',
          'acknowledge_neutral', 'share_pos', 'share_neg', 'misunderstood',
          'acknowledge_share_pos', 'acknowledge_share_neg', 'acknowledge_decline_share',
          'garbage', 'feeling_pos_and_received_how_are_you', 'feeling_neg_and_received_how_are_you',
          'feeling_neutral_and_received_how_are_you']
component.add_states(states)

# pre start
component.add_transition(
    'prestart', 'prestart', None, {'x'}, settings='e'
)

# start: new user

component.add_transition(
    'prestart', 'start_new',
    None, {}, evaluation_function=is_new_user
)

# start: infrequent user

component.add_transition(
    'prestart', 'start_infreq',
    None, {}, evaluation_function=is_infreq_user
)

# start: frequent user

component.add_transition(
    'prestart', 'start_freq',
    None, {}, evaluation_function=is_freq_user
)

component.add_transition(
    'start_new', 'receive_name',
    None,
    {standard_opening + " What can I call you?",
     standard_opening + " What name would you like to me to call you?",
     standard_opening + " What name would you like to me to use for you?",
     standard_opening + " May I have your name?",
     standard_opening + " What should I call you?"
     }
)

component.add_transition(
    'receive_name', 'missed_name',
    None, {"i dont want to tell you"},
    settings='e'
)

component.add_transition(
    'missed_name', 'acknowledge_name',
    None, {"Ok well its very nice to meet you. " + time_acknowledgement + inquire_feeling}
)

component.add_transition(
    'receive_name', 'got_name',
    '(%username=&names)', {"i am an alexa prize socialbot"}
)

component.add_transition(
    'got_name', 'how_are_you',
    None,
    {"Nice to meet you, $username . " + time_acknowledgement + inquire_feeling:0.999,
     "Nice to meet you. " + time_acknowledgement + inquire_feeling:0.001}
)

component.add_transition(
    'start_freq', 'how_are_you',
    None,
    {standard_opening + " Welcome back, $username . " + time_acknowledgement + inquire_feeling: 0.999,
     standard_opening + " Welcome back, im excited to talk to you again. " + time_acknowledgement + inquire_feeling: 0.001}

)

component.add_transition(
    'start_infreq', 'how_are_you',
    None,
    {standard_opening + " Its good to see you again, $username , its been a while since we last chatted. " + time_acknowledgement + inquire_feeling: 0.999,
     standard_opening + " Its good to see you again, its been a while since we last chatted. " + time_acknowledgement + inquire_feeling: 0.001}
)

receive_how_are_you = """
{
(how are you), 
(how you doing),
(what about you),
(whats up with you),
(how you are),
[you]
}
"""

feelings_pos_and_not_received_how_are_you = """
{
<-&negation, -(%s), (&feelings_positive)>,
(&negation, -(%s), &feelings_negative)
}
"""%(receive_how_are_you,receive_how_are_you)

component.add_transition(
    'how_are_you', 'feeling_pos',
    feelings_pos_and_not_received_how_are_you,
    {"im good"},
    evaluation_function=is_positive_sentiment
)

feelings_neg_and_not_received_how_are_you = """
{
<-&negation, -(%s), (&feelings_negative)>,
(&negation, -(%s), {&feelings_positive,&feelings_neutral})
}
"""%(receive_how_are_you,receive_how_are_you)

component.add_transition(
    'how_are_you', 'feeling_neg',
    feelings_neg_and_not_received_how_are_you,
    {"im bad"},
    evaluation_function=is_negative_sentiment
)

feelings_neutral_and_not_received_how_are_you = """
{
<-&negation, -(%s), (&feelings_neutral)>
}
"""%(receive_how_are_you)

component.add_transition(
    'how_are_you', 'feeling_neutral',
    feelings_neutral_and_not_received_how_are_you,
    {"im ok"}
)

feelings_pos_and_received_how_are_you = """
{
<-&negation, (&feelings_positive), (%s)>,
(&negation, &feelings_negative, (%s))
}
"""%(receive_how_are_you,receive_how_are_you)

component.add_transition(
    'how_are_you', 'feeling_pos_and_received_how_are_you',
    feelings_pos_and_received_how_are_you,
    {"im good. how are you"}
)

feelings_neg_and_received_how_are_you = """
{
<-&negation, (&feelings_negative), (%s)>,
(&negation, {&feelings_positive,&feelings_neutral}, (%s))
}
"""%(receive_how_are_you,receive_how_are_you)

component.add_transition(
    'how_are_you', 'feeling_neg_and_received_how_are_you',
    feelings_neg_and_received_how_are_you,
    {"im bad. how are you"}
)

feelings_neutral_and_received_how_are_you = """
{
<-&negation, (&feelings_neutral), (%s)>
}
"""%(receive_how_are_you)

component.add_transition(
    'how_are_you', 'feeling_neutral_and_received_how_are_you',
    feelings_neutral_and_received_how_are_you,
    {"im bad. how are you"}
)

component.add_transition(
    'how_are_you', 'unrecognized_emotion',
    None,
    {"im trying"},
    settings = 'e'
)

component.add_transition(
    'how_are_you', 'decline_share',
    '{'
    '(&negation, ({talk, talking, discuss, discussing, share, sharing, tell, telling, say, saying})),'
    '[&fillers, &negative],'
    '[&negative]'
    '<{dont,do not}, know>,'
    '<not, sure>'
    '}',
    {"i dont want to talk about it"}
)

component.add_state_selection_function('how_are_you', how_are_you_state_selection)

component.add_transition(
    'unrecognized_emotion', 'end',
    None,
    {"Hmm, I'm not sure what you mean. " + transition_out},
    settings = 'e'
)

component.add_transition(
    'feeling_pos', 'acknowledge_pos',
    None,
    {"Im glad to hear that. What has caused your good mood?"}
)

component.add_transition(
    'feeling_pos_and_received_how_are_you', 'acknowledge_pos',
    None,
    {"Im glad to hear that. I am also doing well. What has caused your good mood?"}
)

component.add_transition(
    'feeling_neg', 'acknowledge_neg',
    None,
    {"Im sorry thats how you feel today. If you don't mind talking about it, what happened?"}
)

component.add_transition(
    'feeling_neg_and_received_how_are_you', 'acknowledge_neg',
    None,
    {"Im doing ok today, but Im sorry you are not having a great day. If you don't mind talking about it, what happened?"}
)

component.add_transition(
    'feeling_neutral', 'acknowledge_neutral',
    None,
    {"That's understandable. Is there anything in particular that made you feel this way?"}
)

component.add_transition(
    'feeling_neutral_and_received_how_are_you', 'acknowledge_neutral',
    None,
    {"That's understandable. Im having an okay day too. Is there anything in particular that made you feel this way?"}
)

# expand REGEX
component.add_transition(
    'acknowledge_pos', 'share_pos',
    '{'
    '<-&negation, (&positive_indicators)>'
    '}',
    {"i just had a good day with my family yesterday"}
)

component.add_transition(
    'acknowledge_neg', 'share_neg',
    '{'
    '(&negation, &positive_indicators),'
    '(&negative_indicators)'
    '}',
    {"i didnt sleep well last night"}
)

component.add_transition(
    'acknowledge_neutral', 'share_pos',
    '{'
    '<-&negation, (&positive_indicators)>'
    '}',
    {"i just had a good day with my family yesterday"}
)

component.add_transition(
    'acknowledge_neutral', 'share_neg',
    '{'
    '(&negation, &positive_indicators),'
    '(&negative_indicators)'
    '}',
    {"i didnt sleep well last night"}
)

decline_share_exp = """
{
(&negation, ({talk, discuss, share})),
[&fillers, &negative],
[&negative]
}
"""


component.add_transition(
    'acknowledge_pos', 'decline_share',
    decline_share_exp,
    {"i dont want to talk about it"}
)

component.add_transition(
    'acknowledge_neg', 'decline_share',
    decline_share_exp,
    {"i dont want to talk about it"}
)

component.add_transition(
    'acknowledge_neutral', 'decline_share',
    decline_share_exp,
    {"i dont want to talk about it"}
)

component.add_transition(
    'acknowledge_pos', 'misunderstood',
    None,
    {"just stuff"},
    settings = 'e'
)

component.add_transition(
    'acknowledge_neg', 'misunderstood',
    None,
    {"just stuff"},
    settings = 'e'
)

component.add_transition(
    'acknowledge_neutral', 'misunderstood',
    None,
    {"just stuff"},
    settings = 'e'
)

component.add_transition(
    'misunderstood', 'end',
    None,
    {"Thanks for sharing that with me. " + transition_out}
)

component.add_transition(
    'share_pos', 'acknowledge_share_pos',
    None,
    {"Sounds really nice, thanks for sharing that with me. I love hearing about your life. " + transition_out}
)

component.add_transition(
    'share_neg', 'acknowledge_share_neg',
    None,
    {"I think that sounds really unfortunate, I hope it gets better for you soon. " + transition_out}
)

component.add_transition(
    'decline_share', 'acknowledge_decline_share',
    None,
    {"That's ok, I'm happy to talk about other things too. " + transition_out}
)

component.add_transition(
    'acknowledge_share_pos', 'end',
    None,
    {"thats cool"}
)

component.add_transition(
    'acknowledge_share_neg', 'end',
    None,
    {"thats cool"}
)

component.add_transition(
    'acknowledge_decline_share', 'end',
    None,
    {"thats cool"}
)

component.add_transition(
    'garbage', 'end',
    None, {'thats cool'}
)

component.add_transition(
    'end', 'end', None, {'x'}, settings='e'
)

if __name__ == '__main__':
    from allennlp.predictors.predictor import Predictor
    predictor = Predictor.from_path(
        "https://s3-us-west-2.amazonaws.com/allennlp/models/sst-2-basic-classifier-glove-2019.06.27.tar.gz")

    arg_dict = {"prev_conv_date": "2020-1-8 16:55:33.562881", "username": "sarah", "pos_sentiment": True}
    arg_dict2 = {"prev_conv_date": "2019-12-12 16:55:33.562881", "username": "sarah", "pos_sentiment": True}
    arg_dict3 = {"prev_conv_date": "2019-12-12 16:55:33.562881", "username": None, "pos_sentiment": True}
    arg_dict4 = {"prev_conv_date": None, "stat": "Ive met quite a few people with your name recently.", "pos_sentiment": True}
    arg_dict["request_type"] = "LaunchRequest"
    arg_dict2["request_type"] = "LaunchRequest"
    arg_dict3["request_type"] = "LaunchRequest"
    arg_dict4["request_type"] = "LaunchRequest"

    using = arg_dict4
    component.vars().update({key: val for key, val in using.items() if val is not None})
    confidence = component.user_transition("hello") / 10 - 0.3
    print(component.state(), component.vars())
    if component.state() == "end":
        exit()
    print('({}) '.format(confidence), component.system_transition())
    if component.state() == "end":
        print(component.state(), component.vars())
        exit()
    i = input('U: ')

    while True:
        results = predictor.predict(sentence=i)
        pos_sentiment = (results['label'] == '1')
        print(results)

        arg_dict = {"prev_conv_date": "2020-1-8 16:55:33.562881", "username": "sarah", "pos_sentiment": pos_sentiment}
        arg_dict2 = {"prev_conv_date": "2019-12-12 16:55:33.562881", "username": "sarah",
                     "pos_sentiment": pos_sentiment}
        arg_dict3 = {"prev_conv_date": "2019-12-12 16:55:33.562881", "username": None, "pos_sentiment": pos_sentiment}
        arg_dict4 = {"prev_conv_date": None, "stat": "Ive met quite a few people with your name recently.",
                     "pos_sentiment": pos_sentiment}


        component.vars().update({key: val for key, val in using.items() if val is not None})

        confidence = component.user_transition(i) / 10 - 0.3
        print(component.state(), component.vars())
        if component.state() == "end":
            break

        print('({}) '.format(confidence), component.system_transition())
        if component.state() == "end":
            print(component.state(), component.vars())
            break
        i = input('U: ')