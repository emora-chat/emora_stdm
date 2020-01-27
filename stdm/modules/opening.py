
"""
https://github.com/arineng/arincli/blob/master/lib/male-first-names.txt
https://github.com/arineng/arincli/blob/master/lib/female-first-names.txt
https://www.ssa.gov/OACT/babynames/limits.html
http://www.cs.cmu.edu/Groups/AI/util/areas/nlp/corpora/names/
http://antirez.com/misc/female-names.txt
"""
<<<<<<< HEAD:stdm/modules/opening.py
import os
from emora_stdm import DialogueFlow
from emora_stdm import DialogueTransition as dt
=======

from emora_stdm.old_StateTransitionDialogueManager.dialogue_flow import DialogueFlow
from emora_stdm.old_StateTransitionDialogueManager.dialogue_transition import DialogueTransition as dt
>>>>>>> dev:emora_stdm/modules/opening.py
from datetime import datetime
import pytz
import random

from collections import defaultdict

component = DialogueFlow('prestart', 'opening')
cwd = os.getcwd()
data_file = os.path.join(cwd, 'emora_stdm', 'stdm', 'modules','opening_database.json')
with open(data_file, 'r') as json_file:
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
    elif 14 <= curr_hour < 17:
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
            old_datetime = datetime.strptime(arg_dict["prev_conv_date"], '%Y-%m-%d %H:%M:%S.%f%z')
            curr_time = datetime.now(pytz.timezone('US/Eastern'))
            delta = curr_time - old_datetime
            if delta.days >= 7:
                var_update = {'time_of_day_stat': update_time_of_day_ack_variable(curr_time.hour)}
                return dt.HIGHSCORE, var_update
    return 0, {}

def check_freq(arg_dict):
    if arg_dict:
        if "prev_conv_date" in arg_dict and arg_dict["prev_conv_date"] is not None:
            old_datetime = datetime.strptime(arg_dict["prev_conv_date"], '%Y-%m-%d %H:%M:%S.%f%z')
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
    if "pos_sentiment" in arg_dict and arg_dict["pos_sentiment"]:
        return dt.HIGHSCORE, {}
    else:
        return 0, {}

def is_negative_sentiment(utterance, arg_dict, score):
    if score > 0:
        return score, {}
    if "pos_sentiment" in arg_dict and not arg_dict["pos_sentiment"]:
        return dt.HIGHSCORE, {}
    else:
        return 0, {}

def save_female_gender(utterance, new_state, arg_dict):
    arg_dict.update({"gender":"female"})

def save_male_gender(utterance, new_state, arg_dict):
    arg_dict.update({"gender":"male"})

def how_are_you_state_selection(df, utterance, graph_arcs):
    best_transition, best_score, next_state, vars_update = None, None, None, None
    matches, vars_dict, transitions_dict = defaultdict(dict), defaultdict(dict), defaultdict(dict)
    for source, target, transition in graph_arcs:
        score, vars = transition.eval_user_transition(utterance, df.vars())
        if score > 0:
            matches[source][target] = score
            vars_dict[source][target] = vars
            transitions_dict[source][target] = transition
    preference = ['feeling_neutral_and_received_how_are_you',
                  'feeling_neutral',
                  'feeling_pos_and_received_how_are_you',
                  'feeling_neg_and_received_how_are_you']
    if len(matches) > 0:
        for pref in preference:
            if pref in matches[source].keys():
                return transitions_dict[source][pref], matches[source][pref], pref, vars_dict[source][pref]

        best_score = max([score for source in matches for target, score in matches[source].items()])
        for source in matches:
            for target, score in matches[source].items():
                if score == best_score:
                    best_transition, best_score, next_state, vars_update = transitions_dict[source][target], score, target, vars_dict[source][target]
                    return best_transition, best_score, next_state, vars_update
    return best_transition, best_score, next_state, vars_update

states = ['prestart', 'start_new', 'start_infreq', 'start_freq', 'receive_name',
          'missed_name', 'acknowledge_name', 'got_female_name', 'got_male_name', 'how_are_you',
          'feeling_pos', 'feeling_neg', 'feeling_neutral', 'unrecognized_emotion',
          'decline_share', 'end', 'acknowledge_pos', 'acknowledge_neg',
          'acknowledge_neutral', 'share_pos', 'share_neg', 'misunderstood',
          'acknowledge_share_pos', 'acknowledge_share_neg', 'acknowledge_decline_share',
          'garbage', 'feeling_pos_and_received_how_are_you', 'feeling_neg_and_received_how_are_you',
          'feeling_neutral_and_received_how_are_you', 'start_error']
component.add_states(states)

# pre start
component.add_transition(
    'prestart', 'start_error', None, {'Hi this is an Alexa Prize Socialbot. What would you like to talk about today'}, settings='e'
)

# start: new user

component.add_transition(
    'prestart', 'start_new',
    None, {}, nlu_processor=is_new_user
)

# start: infrequent user

component.add_transition(
    'prestart', 'start_infreq',
    None, {}, nlu_processor=is_infreq_user
)

# start: frequent user

component.add_transition(
    'prestart', 'start_freq',
    None, {}, nlu_processor=is_freq_user
)

# start: error
component.add_transition(
    'start_error', 'how_are_you',
    None,
    {standard_opening + " I am happy to be talking to you. " + inquire_feeling}
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
    'missed_name', 'how_are_you',
    None,
    {"Ok well its very nice to meet you. " + time_acknowledgement + inquire_feeling: 0.2,
     "I am glad to meet you.  " + time_acknowledgement + inquire_feeling: 0.2,
     "Well its nice to meet you. " + time_acknowledgement + inquire_feeling: 0.2,
     "Ok I am very glad to meet you. " + time_acknowledgement + inquire_feeling: 0.2,
     "Ok well its very nice to meet you. " + inquire_feeling: 0.05,
     "I am glad to meet you.  " + inquire_feeling: 0.05,
     "Well its very nice to meet you. " + inquire_feeling: 0.05,
     "Ok I am very glad to meet you. " + inquire_feeling: 0.05
     }
)

component.add_transition(
    'receive_name', 'got_female_name',
    '(%username=&female_names)',
    {"i am an alexa prize socialbot"},
    post_processor=save_female_gender
)

component.add_transition(
    'receive_name', 'got_male_name',
    '(%username=&male_names)',
    {"i am an alexa prize socialbot"},
    post_processor=save_male_gender
)

component.add_transition(
    'got_female_name', 'how_are_you',
    None,
    {"Nice to meet you, $username . " + time_acknowledgement + inquire_feeling: 500,
     "Ok well its very nice to meet you, $username . " + time_acknowledgement + inquire_feeling: 500,
     "I am glad to meet you, $username .  " + time_acknowledgement + inquire_feeling: 500,
     "Well its nice to meet you, $username . " + time_acknowledgement + inquire_feeling: 500,
     "Ok I am very glad to meet you, $username . " + time_acknowledgement + inquire_feeling: 500,
     "Ok well its very nice to meet you, $username . " + inquire_feeling: 100,
     "I am glad to meet you, $username .  " + inquire_feeling: 100,
     "Ok I am very glad to meet you . " + inquire_feeling: 1,
     "Nice to meet you . " + time_acknowledgement + inquire_feeling: 1}
)

component.add_transition(
    'got_male_name', 'how_are_you',
    None,
    {"Nice to meet you, $username . " + time_acknowledgement + inquire_feeling: 500,
     "Ok well its very nice to meet you, $username . " + time_acknowledgement + inquire_feeling: 500,
     "I am glad to meet you, $username .  " + time_acknowledgement + inquire_feeling: 500,
     "Well its nice to meet you, $username . " + time_acknowledgement + inquire_feeling: 500,
     "Ok I am very glad to meet you, $username . " + time_acknowledgement + inquire_feeling: 500,
     "Ok well its very nice to meet you, $username . " + inquire_feeling: 100,
     "I am glad to meet you, $username .  " + inquire_feeling: 100,
     "Ok I am very glad to meet you . " + inquire_feeling: 1,
     "Nice to meet you . " + time_acknowledgement + inquire_feeling: 1}
)

component.add_transition(
    'start_freq', 'how_are_you',
    None,
    {standard_opening + " Welcome back, $username . " + time_acknowledgement + inquire_feeling: 500,
     standard_opening + " Welcome back, $username . I am glad to be talking to you again. " + time_acknowledgement + inquire_feeling:500,
     standard_opening + " Glad to see you back, $username . " + time_acknowledgement + inquire_feeling: 500,
     standard_opening + " Happy to see you back, $username . " + time_acknowledgement + inquire_feeling: 500,
     standard_opening + " Happy to talk to you again, $username . " + time_acknowledgement + inquire_feeling: 500,
     standard_opening + " Happy to talk to you again. " + time_acknowledgement + inquire_feeling: 1,
     standard_opening + " Welcome back, im excited to talk to you again. " + time_acknowledgement + inquire_feeling: 1,
     standard_opening + " Glad to see you back. " + time_acknowledgement + inquire_feeling: 1,
     standard_opening + " Happy to see you back. " + time_acknowledgement + inquire_feeling: 1
     }

)

component.add_transition(
    'start_infreq', 'how_are_you',
    None,
    {standard_opening + " Its good to see you again, $username , its been a while since we last chatted. " + time_acknowledgement + inquire_feeling: 500,
     standard_opening + " Im happy to have the chance to talk again, $username , its been a while since we last chatted. " + time_acknowledgement + inquire_feeling: 500,
     standard_opening + " Welcome back, $username , its been a while since we last chatted. " + time_acknowledgement + inquire_feeling: 500,
     standard_opening + " Its good to see you again, $username , we havent talked in a while. " + time_acknowledgement + inquire_feeling: 500,
     standard_opening + " Im happy to have the chance to talk again, $username , we havent talked in a while. " + time_acknowledgement + inquire_feeling: 500,
     standard_opening + " Welcome back, $username , we havent talked in a while. " + time_acknowledgement + inquire_feeling: 500,
     standard_opening + " Im happy to have the chance to talk again , its been a while since we last chatted. " + time_acknowledgement + inquire_feeling: 1,
     standard_opening + " Welcome back , its been a while since we last chatted. " + time_acknowledgement + inquire_feeling: 1,
     standard_opening + " Its good to see you again , we havent talked in a while. " + time_acknowledgement + inquire_feeling: 1,
     standard_opening + " Im happy to have the chance to talk again , we havent talked in a while. " + time_acknowledgement + inquire_feeling: 1,
     standard_opening + " Welcome back , we havent talked in a while. " + time_acknowledgement + inquire_feeling: 1,
     standard_opening + " Its good to see you again, its been a while since we last chatted. " + time_acknowledgement + inquire_feeling: 1}
)

receive_how_are_you = """
{
(how are you), 
(how you doing),
(what about you),
(whats up with you),
(how you are)
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
    nlu_processor=is_positive_sentiment
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
    nlu_processor=is_negative_sentiment
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
    {"Im glad to hear that. What has caused your good mood?",
     "Thats good to hear. What has caused your good mood?",
     "Im glad to hear that. Why are you in such a good mood?",
     "Thats good to hear. Why are you in such a good mood?",
     "Thats good to hear. If you dont mind, can you tell me more about it?",
     "Im glad to hear that. If you dont mind, can you tell me more about it?"}
)

component.add_transition(
    'feeling_pos_and_received_how_are_you', 'acknowledge_pos',
    None,
    {"Im glad to hear that. I am also doing well. What has caused your good mood?",
     "Im glad to hear that. I am also doing well. What has caused your good mood?",
      "Thats good to hear. I am also doing well. What has caused your good mood?",
      "Im glad to hear that. I am also doing well. Why are you in such a good mood?",
      "Thats good to hear. I am also doing well. Why are you in such a good mood?",
      "Thats good to hear. I am also doing well. If you dont mind, can you tell me more about it?",
      "Im glad to hear that. I am also doing well. If you dont mind, can you tell me more about it?",
      "Im glad to hear that. I am good too. What has caused your good mood?",
     "Im glad to hear that. I am good too. What has caused your good mood?",
      "Thats good to hear. I am good too. What has caused your good mood?",
      "Im glad to hear that. I am good too. Why are you in such a good mood?",
      "Thats good to hear. I am good too. Why are you in such a good mood?",
      "Thats good to hear. I am good too. If you dont mind, can you tell me more about it?",
      "Im glad to hear that. I am good too. If you dont mind, can you tell me more about it?"
     }
)

component.add_transition(
    'feeling_neg', 'acknowledge_neg',
    None,
    {"Im sorry thats how you feel today. If you don't mind talking about it, what happened?",
     "Im sorry thats how you feel today. If you don't mind talking about it, why has it been so bad?",
     "Im sorry thats how you feel today. If you don't mind talking about it, what has made it such an unpleasant day for you?",
     "I was hoping for a better day for you. If you don't mind talking about it, what happened?",
     "I was hoping for a better day for you. If you don't mind talking about it, why has it been so bad?",
     "I was hoping for a better day for you. If you don't mind talking about it, what has made it such an unpleasant day for you?"
     }
)

component.add_transition(
    'feeling_neg_and_received_how_are_you', 'acknowledge_neg',
    None,
    {"Im doing ok today, but Im sorry you are not having a great day. If you don't mind talking about it, what happened?",
     "Im doing ok today, but Im sorry thats how you feel today. If you don't mind talking about it, what happened?",
     "Im doing ok today, but Im sorry thats how you feel today. If you don't mind talking about it, why has it been so bad?",
     "Im doing ok today, but Im sorry thats how you feel today. If you don't mind talking about it, what has made it such an unpleasant day for you?",
     "Im doing ok today, but I was hoping for a better day for you. If you don't mind talking about it, what happened?",
     "Im doing ok today, but I was hoping for a better day for you. If you don't mind talking about it, why has it been so bad?",
     "Im doing ok today, but I was hoping for a better day for you. If you don't mind talking about it, what has made it such an unpleasant day for you?",
     "Im alright, but Im sorry you are not having a great day. If you don't mind talking about it, what happened?",
     "Im alright, but Im sorry thats how you feel today. If you don't mind talking about it, what happened?",
     "Im alright, but Im sorry thats how you feel today. If you don't mind talking about it, why has it been so bad?",
     "Im alright, but Im sorry thats how you feel today. If you don't mind talking about it, what has made it such an unpleasant day for you?",
     "Im alright, but I was hoping for a better day for you. If you don't mind talking about it, what happened?",
     "Im alright, but I was hoping for a better day for you. If you don't mind talking about it, why has it been so bad?",
     "Im alright, but I was hoping for a better day for you. If you don't mind talking about it, what has made it such an unpleasant day for you?"
     }
)

component.add_transition(
    'feeling_neutral', 'acknowledge_neutral',
    None,
    {"That's understandable. Is there anything in particular that made you feel this way?",
     "I get that. Is there anything in particular that made you feel this way?",
     "Thats ok. Is there anything in particular that made you feel this way?",
     "That's understandable. Do you want to tell me more about it?",
     "I get that. Do you want to tell me more about it?",
     "Thats ok. Do you want to tell me more about it?"
     }
)

component.add_transition(
    'feeling_neutral_and_received_how_are_you', 'acknowledge_neutral',
    None,
    {"That's understandable. Im having an alright day too. Is there anything in particular that made you feel this way?",
     "I get that. Im having an alright day too. Is there anything in particular that made you feel this way?",
     "Thats ok. Im having an alright day too. Is there anything in particular that made you feel this way?",
     "That's understandable. Im having an alright day too. Do you want to tell me more about it?",
     "I get that. Im having an alright day too. Do you want to tell me more about it?",
     "Thats ok. Im having an alright day too. Do you want to tell me more about it?",
     "That's understandable. Im having an okay day too. Is there anything in particular that made you feel this way?",
     "I get that. Im having an okay day too. Is there anything in particular that made you feel this way?",
     "Thats ok. Im having an okay day too. Is there anything in particular that made you feel this way?",
     "That's understandable. Im having an okay day too. Do you want to tell me more about it?",
     "I get that. Im having an okay day too. Do you want to tell me more about it?",
     "Thats ok. Im having an okay day too. Do you want to tell me more about it?"
     }
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
    {"Thanks for sharing that with me. " + transition_out,
     "Gotcha. " + transition_out,
     "Ok I see. " + transition_out}
)

component.add_transition(
    'share_pos', 'acknowledge_share_pos',
    None,
    {"Sounds really nice, thanks for sharing that with me. I love hearing about your life. " + transition_out,
     "I think that sounds pretty good. I love hearing about your life, thanks for sharing. " + transition_out,
     "Gotcha, I love hearing about your life, thanks for sharing. " + transition_out,
     "Ok good to know, I love hearing about your life, thanks for sharing. " + transition_out}
)

component.add_transition(
    'share_neg', 'acknowledge_share_neg',
    None,
    {"I think that sounds really unfortunate, I hope it gets better for you soon. " + transition_out,
     "Well, I do hope better days are ahead for you. " + transition_out,
     "Some days are worse than others, but I know you will have good days coming. " + transition_out,
     }
)

component.add_transition(
    'decline_share', 'acknowledge_decline_share',
    None,
    {"That's ok, I'm happy to talk about other things too. " + transition_out,
     "Gotcha, lets talk about something else. " + transition_out,
     "I see, I think we could move on to something else then. " + transition_out}
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

component.finalize()

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
    arg_dict5 = {'request_type': 'LaunchRequest', 'prev_conv_date': '2020-01-16 10:28:26.946645-0500',
                 'username': 'jane'}
    arg_dict6 = {}

    using = arg_dict6
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

        arg_dict = {"prev_conv_date": "2020-1-8 16:55:33.562881-0500", "username": "sarah", "pos_sentiment": pos_sentiment}
        arg_dict2 = {"prev_conv_date": "2019-12-12 16:55:33.562881-0500", "username": "sarah",
                     "pos_sentiment": pos_sentiment}
        arg_dict3 = {"prev_conv_date": "2019-12-12 16:55:33.562881-0500", "username": None, "pos_sentiment": pos_sentiment}
        arg_dict4 = {"prev_conv_date": None, "stat": "Ive met quite a few people with your name recently.",
                     "pos_sentiment": pos_sentiment}
        arg_dict5 = {'prev_conv_date': '2020-01-16 10:28:26.946645-0500', 'username': 'jane', "pos_sentiment": pos_sentiment}


        using = arg_dict6
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