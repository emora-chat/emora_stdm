
"""
https://github.com/arineng/arincli/blob/master/lib/male-first-names.txt
https://github.com/arineng/arincli/blob/master/lib/female-first-names.txt
https://www.ssa.gov/OACT/babynames/limits.html
http://www.cs.cmu.edu/Groups/AI/util/areas/nlp/corpora/names/
http://antirez.com/misc/female-names.txt
"""

from emora_stdm import DialogueFlow, KnowledgeBase, Macro
from datetime import datetime
import pytz
import random

NULL = "NULL TRANSITION"

def check_launch_request(arg_dict):
    if "request_type" in arg_dict and arg_dict["request_type"] == "LaunchRequest":
        return True
    return False

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

class IsNewUser(Macro):
    def run(self, ngrams, vars, args):
        if check_launch_request(vars):
            if "prev_conv_date" not in vars or vars["prev_conv_date"] is None:
                vars['time_of_day_stat'] = update_time_of_day_ack_variable()
                vars['user_type'] = 'new'
                return True
        return False

class IsInfreqUserWithName(Macro):
    def run(self, ngrams, vars, args):
        if check_launch_request(vars) and 'username' in vars and vars['username'] is not None:
            if "prev_conv_date" in vars and vars["prev_conv_date"] is not None:
                old_datetime = datetime.strptime(vars["prev_conv_date"], '%Y-%m-%d %H:%M:%S.%f%z')
                curr_time = datetime.now(pytz.timezone('US/Eastern'))
                delta = curr_time - old_datetime
                if delta.days >= 7:
                    vars['time_of_day_stat'] = update_time_of_day_ack_variable(curr_time.hour)
                    vars['user_type'] = 'infreq'
                    return True
        return False

class IsInfreqUser(Macro):
    def run(self, ngrams, vars, args):
        if check_launch_request(vars):
            if "prev_conv_date" in vars and vars["prev_conv_date"] is not None:
                old_datetime = datetime.strptime(vars["prev_conv_date"], '%Y-%m-%d %H:%M:%S.%f%z')
                curr_time = datetime.now(pytz.timezone('US/Eastern'))
                delta = curr_time - old_datetime
                if delta.days >= 7:
                    vars['time_of_day_stat'] = update_time_of_day_ack_variable(curr_time.hour)
                    vars['user_type'] = 'infreq'
                    return True
        return False

class IsFreqUserWithName(Macro):
    def run(self, ngrams, vars, args):
        if check_launch_request(vars) and 'username' in vars and vars['username'] is not None:
            if "prev_conv_date" in vars and vars["prev_conv_date"] is not None:
                old_datetime = datetime.strptime(vars["prev_conv_date"], '%Y-%m-%d %H:%M:%S.%f%z')
                curr_time = datetime.now(pytz.timezone('US/Eastern'))
                delta = curr_time - old_datetime
                if delta.days < 7:
                    vars['time_of_day_stat'] = update_time_of_day_ack_variable(curr_time.hour)
                    vars['user_type'] = 'freq'
                    return True
        return False

class IsFreqUser(Macro):
    def run(self, ngrams, vars, args):
        if check_launch_request(vars):
            if "prev_conv_date" in vars and vars["prev_conv_date"] is not None:
                old_datetime = datetime.strptime(vars["prev_conv_date"], '%Y-%m-%d %H:%M:%S.%f%z')
                curr_time = datetime.now(pytz.timezone('US/Eastern'))
                delta = curr_time - old_datetime
                if delta.days < 7:
                    vars['time_of_day_stat'] = update_time_of_day_ack_variable(curr_time.hour)
                    vars['user_type'] = 'freq'
                    return True
        return False

class IsPositiveSentiment(Macro):
    def run(self, ngrams, vars, args):
        if "sentiment_type" in vars and vars["sentiment_type"] == 'pos':
            return True
        return False

class IsNegativeSentiment(Macro):
    def run(self, ngrams, vars, args):
        if "sentiment_type" in vars and vars["sentiment_type"] == 'neg':
            return True
        return False

class SaveFemaleGender(Macro):
    def run(self, ngrams, vars, args):
        vars['gender'] = 'female'

class SaveMaleGender(Macro):
    def run(self, ngrams, vars, args):
        vars['gender'] = 'male'


knowledge = KnowledgeBase()
knowledge.load_json_file('opening_database.json')
macros = {
    "IsNewUser": IsNewUser(),
    "IsFreqUser": IsFreqUser(),
    "IsInfreqUser": IsInfreqUser(),
    "IsFreqUserWithName": IsFreqUserWithName(),
    "IsInfreqUserWithName": IsInfreqUserWithName(),
    "IsPositiveSentiment": IsPositiveSentiment(),
    "IsNegativeSentiment": IsNegativeSentiment(),
    "SaveFemaleGender": SaveFemaleGender(),
    "SaveMaleGender": SaveMaleGender()
}
component = DialogueFlow('prestart', initial_speaker=DialogueFlow.Speaker.USER, macros=macros, kb=knowledge)

standard_opening = 'Hi"," this is an Alexa Prize Socialbot"."'
inquire_feeling = 'How are you today"?"'
time_acknowledgement = '$time_of_day_stat "." '
transition_out = '"What would you like to talk about today? Ive recently started learning about fun hobbies and sports, but I also know a lot about movies and music."'


# start

component.add_user_transition('prestart', 'start_new', r'#IsNewUser')
component.add_user_transition('prestart', 'start_infreq', r'#IsInfreqUser')
component.add_user_transition('prestart', 'start_freq', r'#IsFreqUser')
component.add_user_transition('prestart', 'start_infreq_with_name', r'#IsInfreqUserWithName', score=1.1)
component.add_user_transition('prestart', 'start_freq_with_name', r'#IsFreqUserWithName', score=1.1)
component.set_error_successor('prestart', 'start_error')


component.add_system_transition('start_error', 'how_are_you', "[!" + standard_opening + r' I am happy to be talking to you"." ' + inquire_feeling + "]")

component.add_system_transition('start_new', 'receive_name',
    ["[!" + standard_opening + ' What can I call you"?"]',
     "[!" + standard_opening + ' What name would you like to me to call you"?"]',
     "[!" + standard_opening + ' What name would you like to me to use for you"?"]',
     "[!" + standard_opening + ' May I have your name"?"]',
     "[!" + standard_opening + ' What should I call you"?"]'
     ]
)
component.add_user_transition('receive_name', 'got_female_name', r'[$username=#ONT(ont_female_names) #SaveFemaleGender]')
component.add_user_transition('receive_name', 'got_male_name', r'[$username=#ONT(ont_male_names) #SaveMaleGender]')
component.set_error_successor('receive_name', 'missed_name')

component.add_system_transition('missed_name', 'how_are_you',
    ['[!Ok"," well its very nice to meet you"." ' + time_acknowledgement + inquire_feeling + "]",
     '[!I am glad to meet you"." ' + time_acknowledgement + inquire_feeling + "]",
     '[!Well"," its nice to meet you"." ' + time_acknowledgement + inquire_feeling + "]",
     '[!Ok"," I am very glad to meet you"." ' + time_acknowledgement + inquire_feeling + "]",
     '[!Ok"," well its very nice to meet you"." ' + inquire_feeling + "]",
     '[!I am glad to meet you"." ' + inquire_feeling + "]",
     '[!Well"," its very nice to meet you"." ' + inquire_feeling + "]",
     '[!Ok"," I am very glad to meet you"." ' + inquire_feeling + "]"
     ]
)

component.add_system_transition('got_female_name', 'how_are_you',
    ['[!Ok"," well its very nice to meet you","$username"." ' + time_acknowledgement + inquire_feeling + "]",
     '[!I am glad to meet you","$username"." ' + time_acknowledgement + inquire_feeling + "]",
     '[!Well its nice to meet you","$username"." ' + time_acknowledgement + inquire_feeling + "]",
     '[!Ok"," I am very glad to meet you","$username"." ' + time_acknowledgement + inquire_feeling + "]",
     '[!Ok"," well its very nice to meet you","$username"." ' + inquire_feeling + "]",
     '[!I am glad to meet you","$username"." ' + inquire_feeling + "]",
     '[!Well its very nice to meet you","$username"." ' + inquire_feeling + "]",
     '[!Ok"," I am very glad to meet you","$username"." ' + inquire_feeling + "]"
     ]
)

component.add_system_transition('got_male_name', 'how_are_you',
    ['[!Ok"," well its very nice to meet you","$username"." ' + time_acknowledgement + inquire_feeling + "]",
     '[!I am glad to meet you","$username"." ' + time_acknowledgement + inquire_feeling + "]",
     '[!Well its nice to meet you","$username"." ' + time_acknowledgement + inquire_feeling + "]",
     '[!Ok"," I am very glad to meet you","$username"." ' + time_acknowledgement + inquire_feeling + "]",
     '[!Ok"," well its very nice to meet you","$username"." ' + inquire_feeling + "]",
     '[!I am glad to meet you","$username"." ' + inquire_feeling + "]",
     '[!Well its very nice to meet you","$username"." ' + inquire_feeling + "]",
     '[!Ok"," I am very glad to meet you","$username"." ' + inquire_feeling + "]"
     ]
)

component.add_system_transition('start_freq_with_name', 'how_are_you',
    ["[!" + standard_opening + ' Welcome back"," $username"." ' + time_acknowledgement + inquire_feeling + "]",
     "[!" + standard_opening + ' Welcome back"," $username"." I am glad to be talking to you again"." ' + time_acknowledgement + inquire_feeling + "]",
     "[!" + standard_opening + ' Glad to see you back"," $username"." ' + time_acknowledgement + inquire_feeling + "]",
     "[!" + standard_opening + ' Happy to see you back"," $username"." ' + time_acknowledgement + inquire_feeling + "]",
     "[!" + standard_opening + ' Happy to talk to you again"," $username"." ' + time_acknowledgement + inquire_feeling + "]"]

)

component.add_system_transition('start_freq', 'how_are_you',
    [ "[!" + standard_opening + ' Happy to talk to you again"." ' + time_acknowledgement + inquire_feeling + "]",
        "[!" + standard_opening + ' Welcome back"," im excited to talk to you again"." ' + time_acknowledgement + inquire_feeling + "]",
        "[!" + standard_opening + ' Glad to see you back"." ' + time_acknowledgement + inquire_feeling + "]",
        "[!" + standard_opening + ' Happy to see you back"." ' + time_acknowledgement + inquire_feeling + "]"]
)

component.add_system_transition('start_infreq_with_name', 'how_are_you',
    ["[!" + standard_opening + ' Its good to see you again"," $username "," its been a while since we last chatted"." ' + time_acknowledgement + inquire_feeling + "]",
     "[!" + standard_opening + ' Im happy to have the chance to talk again"," $username "," its been a while since we last chatted"." ' + time_acknowledgement + inquire_feeling + "]",
     "[!" + standard_opening + ' Welcome back"," $username "," its been a while since we last chatted"." ' + time_acknowledgement + inquire_feeling + "]",
     "[!" + standard_opening + ' Its good to see you again"," $username "," we havent talked in a while"." ' + time_acknowledgement + inquire_feeling + "]",
     "[!" + standard_opening + ' Im happy to have the chance to talk again"," $username "," we havent talked in a while"." ' + time_acknowledgement + inquire_feeling + "]",
     "[!" + standard_opening + ' Welcome back"," $username "," we havent talked in a while"." ' + time_acknowledgement + inquire_feeling + "]",
     ]
)

component.add_system_transition('start_infreq', 'how_are_you',
    ["[!" + standard_opening + ' Im happy to have the chance to talk again "," its been a while since we last chatted"." ' + time_acknowledgement + inquire_feeling + "]",
     "[!" + standard_opening + ' Welcome back "," its been a while since we last chatted"." ' + time_acknowledgement + inquire_feeling + "]",
     "[!" + standard_opening + ' Its good to see you again "," we havent talked in a while"." ' + time_acknowledgement + inquire_feeling + "]",
     "[!" + standard_opening + ' Im happy to have the chance to talk again "," we havent talked in a while"." ' + time_acknowledgement + inquire_feeling + "]",
     "[!" + standard_opening + ' Welcome back "," we havent talked in a while"." ' + time_acknowledgement + inquire_feeling + "]",
     "[!" + standard_opening + ' Its good to see you again"," its been a while since we last chatted"." ' + time_acknowledgement + inquire_feeling + "]"]
)

receive_how_are_you = "{" \
                      "[how are you]," \
                      "[how you doing]," \
                      "[what about you]," \
                      "[whats up with you]," \
                      "[how you are]," \
                      "[how about you]" \
                      "}"

feelings_pos_and_not_received_how_are_you = "{" \
                                                "[!#ONT_NEG(ont_negation), -%s, [#ONT(ont_feelings_positive)]]," \
                                                "[! -%s, [#ONT(ont_negation)], [#ONT(ont_feelings_negative)]]," \
                                                "#IsPositiveSentiment" \
                                                "}" % (receive_how_are_you, receive_how_are_you)


feelings_neg_and_not_received_how_are_you = "{" \
                                            "[!#ONT_NEG(ont_negation), -%s, [#ONT(ont_feelings_negative)]]," \
                                            "[! -%s, [#ONT(ont_negation)], [{#ONT(ont_feelings_positive),#ONT(ont_feelings_neutral)}]]," \
                                            "#IsNegativeSentiment" \
                                            "}" % (receive_how_are_you, receive_how_are_you)

feelings_neutral_and_not_received_how_are_you = "[!#ONT_NEG(ont_negation), -%s, [#ONT(ont_feelings_neutral)]]" % (
        receive_how_are_you)
feelings_pos_and_received_how_are_you = "{" \
                                        "[!#ONT_NEG(ont_negation), [#ONT(ont_feelings_positive)], [%s]]," \
                                        "[#ONT(ont_negation), #ONT(ont_feelings_negative), %s]," \
                                        "<#IsPositiveSentiment, %s>" \
                                        "}" % (receive_how_are_you, receive_how_are_you, receive_how_are_you)

feelings_neg_and_received_how_are_you = "{" \
                                            "[!#ONT_NEG(ont_negation), [#ONT(ont_feelings_negative)], [%s]]," \
                                            "[#ONT(ont_negation), {#ONT(ont_feelings_positive),#ONT(ont_feelings_neutral)}, %s]," \
                                            "<#IsNegativeSentiment, %s>" \
                                            "}" % (receive_how_are_you, receive_how_are_you, receive_how_are_you)

feelings_neutral_and_received_how_are_you = "[!#ONT_NEG(ont_negation), [#ONT(ont_feelings_neutral)], [%s]]" % (
    receive_how_are_you)
decline_share = "{" \
                "[#ONT(ont_negation), {talk, talking, discuss, discussing, share, sharing, tell, telling, say, saying}]," \
                "[#ONT(ont_fillers), #ONT(ont_negative)]," \
                "[#ONT(ont_negative)]" \
                "<{dont,do not}, know>," \
                "<not, sure>" \
                "}"


component.add_user_transition('how_are_you', 'feeling_pos', feelings_pos_and_not_received_how_are_you,score=1.0)
component.add_user_transition('how_are_you', 'feeling_neg', feelings_neg_and_not_received_how_are_you,score=1.0)
component.add_user_transition('how_are_you', 'feeling_neutral', feelings_neutral_and_not_received_how_are_you,score=1.1)
component.add_user_transition('how_are_you', 'feeling_pos_and_received_how_are_you', feelings_pos_and_received_how_are_you,score=1.2)
component.add_user_transition('how_are_you', 'feeling_neg_and_received_how_are_you', feelings_neg_and_received_how_are_you, score=1.2)
component.add_user_transition('how_are_you', 'feeling_neutral_and_received_how_are_you',feelings_neutral_and_received_how_are_you, score=1.3)
component.add_user_transition('how_are_you', 'decline_share', decline_share)

component.set_error_successor('how_are_you', 'unrecognized_emotion')

component.add_system_transition('unrecognized_emotion', 'end','[!Hmm"," Im not sure what you mean"." ' + transition_out + "]")

component.add_system_transition('feeling_pos', 'acknowledge_pos',
    ['[!Im glad to hear that"." What has caused your good mood"?"]',
     '[!Thats good to hear"." What has caused your good mood"?"]',
     '[!Im glad to hear that"." Why are you in such a good mood"?"]',
     '[!Thats good to hear"." Why are you in such a good mood"?"]',
     '[!Thats good to hear"." If you dont mind"," can you tell me more about it"?"]',
     '[!Im glad to hear that"." If you dont mind"," can you tell me more about it"?"]']
)

component.add_system_transition('feeling_pos_and_received_how_are_you', 'acknowledge_pos',
    ['[!Im glad to hear that"." I am also doing well"." What has caused your good mood"?"]',
     '[!Im glad to hear that"." I am also doing well"." What has caused your good mood"?"]',
      '[!Thats good to hear"." I am also doing well"." What has caused your good mood"?"]',
      '[!Im glad to hear that"." I am also doing well"." Why are you in such a good mood"?"]',
      '[!Thats good to hear"." I am also doing well"." Why are you in such a good mood"?"]',
      '[!Thats good to hear"." I am also doing well"." If you dont mind"," can you tell me more about it"?"]',
      '[!Im glad to hear that"." I am also doing well"." If you dont mind"," can you tell me more about it"?"]',
      '[!Im glad to hear that"." I am good too"." What has caused your good mood"?"]',
      '[!Im glad to hear that"." I am good too"." What has caused your good mood"?"]',
      '[!Thats good to hear"." I am good too"." What has caused your good mood"?"]',
      '[!Im glad to hear that"." I am good too"." Why are you in such a good mood"?"]',
      '[!Thats good to hear"." I am good too"." Why are you in such a good mood"?"]',
      '[!Thats good to hear"." I am good too"." If you dont mind"," can you tell me more about it"?"]',
      '[!Im glad to hear that"." I am good too"." If you dont mind"," can you tell me more about it"?"]'
     ]
)

component.add_system_transition('feeling_neg', 'acknowledge_neg',
    ['[!Im sorry thats how you feel today"." If you dont mind talking about it"," what happened"?"]',
     '[!Im sorry thats how you feel today"." If you dont mind talking about it"," why has it been so bad"?"]',
     '[!Im sorry thats how you feel today"." If you dont mind talking about it"," what has made it such an unpleasant day for you"?"]',
     '[!I was hoping for a better day for you"." If you dont mind talking about it"," what happened"?"]',
     '[!I was hoping for a better day for you"." If you dont mind talking about it"," why has it been so bad"?"]',
     '[!I was hoping for a better day for you"." If you dont mind talking about it"," what has made it such an unpleasant day for you"?"]'
     ]
)

component.add_system_transition('feeling_neg_and_received_how_are_you', 'acknowledge_neg',
    ['[!Im doing ok today"," but Im sorry you are not having a great day"." If you dont mind talking about it"," what happened"?"]',
     '[!Im doing ok today"," but Im sorry thats how you feel today"." If you dont mind talking about it"," what happened"?"]',
     '[!Im doing ok today"," but Im sorry thats how you feel today"." If you dont mind talking about it"," why has it been so bad"?"]',
     '[!Im doing ok today"," but Im sorry thats how you feel today"." If you dont mind talking about it"," what has made it such an unpleasant day for you"?"]',
     '[!Im doing ok today"," but I was hoping for a better day for you"." If you dont mind talking about it"," what happened"?"]',
     '[!Im doing ok today"," but I was hoping for a better day for you"." If you dont mind talking about it"," why has it been so bad"?"]',
     '[!Im doing ok today"," but I was hoping for a better day for you"." If you dont mind talking about it"," what has made it such an unpleasant day for you"?"]',
     '[!Im alright"," but Im sorry you are not having a great day"." If you dont mind talking about it"," what happened"?"]',
     '[!Im alright"," but Im sorry thats how you feel today"." If you dont mind talking about it"," what happened"?"]',
     '[!Im alright"," but Im sorry thats how you feel today"." If you dont mind talking about it"," why has it been so bad"?"]',
     '[!Im alright"," but Im sorry thats how you feel today"." If you dont mind talking about it"," what has made it such an unpleasant day for you"?"]',
     '[!Im alright"," but I was hoping for a better day for you"." If you dont mind talking about it"," what happened"?"]',
     '[!Im alright"," but I was hoping for a better day for you"." If you dont mind talking about it"," why has it been so bad"?"]',
     '[!Im alright"," but I was hoping for a better day for you"." If you dont mind talking about it"," what has made it such an unpleasant day for you"?"]'
     ]
)

component.add_system_transition('feeling_neutral', 'acknowledge_neutral',
    ['[!Thats understandable"." Is there anything in particular that made you feel this way"?"]',
     '[!I get that"." Is there anything in particular that made you feel this way"?"]',
     '[!Thats ok"." Is there anything in particular that made you feel this way"?"]',
     '[!Thats understandable"." Do you want to tell me more about it"?"]',
     '[!I get that"." Do you want to tell me more about it"?"]',
     '[!Thats ok"." Do you want to tell me more about it"?"]'
     ]
)

component.add_system_transition('feeling_neutral_and_received_how_are_you', 'acknowledge_neutral',
    ['[!Thats understandable"." Im having an alright day too"." Is there anything in particular that made you feel this way"?"]',
     '[!I get that"." Im having an alright day too"." Is there anything in particular that made you feel this way"?"]',
     '[!Thats ok"." Im having an alright day too"." Is there anything in particular that made you feel this way"?"]',
     '[!Thats understandable"." Im having an alright day too"." Do you want to tell me more about it"?"]',
     '[!I get that"." Im having an alright day too"." Do you want to tell me more about it"?"]',
     '[!Thats ok"." Im having an alright day too"." Do you want to tell me more about it"?"]',
     '[!Thats understandable"." Im having an okay day too"." Is there anything in particular that made you feel this way"?"]',
     '[!I get that"." Im having an okay day too"." Is there anything in particular that made you feel this way"?"]',
     '[!Thats ok"." Im having an okay day too"." Is there anything in particular that made you feel this way"?"]',
     '[!Thats understandable"." Im having an okay day too"." Do you want to tell me more about it"?"]',
     '[!I get that"." Im having an okay day too"." Do you want to tell me more about it"?"]',
     '[!Thats ok"." Im having an okay day too"." Do you want to tell me more about it"?"]'
     ]
)

component.add_user_transition('acknowledge_pos', 'share_pos',
    '{'
    '[!#ONT_NEG(ont_negation), [#ONT(ont_positive_indicators)]]'
    '}'
)

component.add_user_transition('acknowledge_neg', 'share_neg',
    '{'
    '[#ONT(ont_negation), #ONT(ont_positive_indicators)],'
    '[#ONT(ont_negative_indicators)]'
    '}'
)

component.add_user_transition('acknowledge_neutral', 'share_pos',
    '{'
    '[!#ONT_NEG(ont_negation), [#ONT(ont_positive_indicators)]]'
    '}'
)

component.add_user_transition('acknowledge_neutral', 'share_neg',
    '{'
    '[#ONT(ont_negation), #ONT(ont_positive_indicators)],'
    '[#ONT(ont_negative_indicators)]'
    '}'
)


component.add_user_transition('acknowledge_pos', 'decline_share', decline_share)
component.add_user_transition('acknowledge_neg', 'decline_share', decline_share)
component.add_user_transition('acknowledge_neutral', 'decline_share', decline_share)
component.set_error_successor('acknowledge_pos', 'misunderstood')
component.set_error_successor('acknowledge_neg', 'misunderstood')
component.set_error_successor('acknowledge_neutral', 'misunderstood')


component.add_system_transition('misunderstood', 'end',
    ['[!Thanks for sharing that with me"." ' + transition_out + "]",
     '[!Gotcha"." ' + transition_out + "]",
     '[!Ok"," I see"." ' + transition_out + "]"]
)

component.add_system_transition('share_pos', 'acknowledge_share_pos',
    ['[!Sounds really nice"." Thanks for sharing that with me"." ' + transition_out + "]",
     '[!I think that sounds pretty good"." I love hearing about your life"." ' + transition_out + "]",
     '[!Gotcha"." I love hearing about your life"." Thanks for sharing"." ' + transition_out + "]",
     '[!Ok"," good to know"." Thanks for sharing"." ' + transition_out + "]"]
)

component.add_system_transition('share_neg', 'acknowledge_share_neg',
    ['[!I think that sounds really unfortunate"." I hope it gets better for you soon"." ' + transition_out + "]",
     '[!Well"," I do hope better days are ahead for you"." ' + transition_out + "]",
     '[!Some days are worse than others"," but I know you will have good days coming"." ' + transition_out + "]",
     ]
)

component.add_system_transition('decline_share', 'acknowledge_decline_share',
    ['[!Thats ok"." Im happy to talk about other things too"." ' + transition_out + "]",
     '[!Gotcha"." Lets talk about something else then"." ' + transition_out + "]",
     '[!I see"." I think we could move on to something else then"." ' + transition_out + "]"]
)

component.set_error_successor('acknowledge_share_pos', 'end')
component.set_error_successor('acknowledge_share_neg', 'end')
component.set_error_successor('acknowledge_decline_share', 'end')
component.set_error_successor('end', 'end')
component.add_system_transition('end', 'end', NULL)

if __name__ == '__main__':

    arg_dict = {'request_type': 'LaunchRequest',"prev_conv_date": "2020-1-28 16:55:33.562881-0500", "username": "sarah", "sentiment_type": "pos"}
    arg_dict2 = {'request_type': 'LaunchRequest',"prev_conv_date": "2019-12-12 16:55:33.562881-0500", "username": "sarah","sentiment_type": "pos"}
    arg_dict3 = {'request_type': 'LaunchRequest',"prev_conv_date": "2019-12-12 16:55:33.562881-0500", "username": None, "sentiment_type": "pos"}
    arg_dict4 = {'request_type': 'LaunchRequest',"prev_conv_date": None}
    arg_dict5 = {'request_type': 'LaunchRequest', 'prev_conv_date': '2020-01-16 10:28:26.946645-0500','username': 'jane'}
    arg_dict6 = {'request_type': 'LaunchRequest', 'sentiment_type': 'neg', 'prev_conv_date': '2020-01-10 10:58:50.175772-0500'}

    using = arg_dict4
    component._vars.update({key: val for key, val in using.items() if val is not None})

    component.run(debugging=False)