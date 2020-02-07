
"""
https://github.com/arineng/arincli/blob/master/lib/male-first-names.txt
https://github.com/arineng/arincli/blob/master/lib/female-first-names.txt
https://www.ssa.gov/OACT/babynames/limits.html
http://www.cs.cmu.edu/Groups/AI/util/areas/nlp/corpora/names/
http://antirez.com/misc/female-names.txt
"""

from emora_stdm import DialogueFlow, KnowledgeBase, Macro
from GlobalUserTableAccessor import GlobalUserTableAccessor
from datetime import datetime
import pytz,random

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

emotions = ["happy", "sad", "neutral"]
probs = [0.70,0.29,0.01]

environ_personality = {
    'neutral':{
        'morning': ['its pretty early in the morning for me', 'its pretty early where I am'],
        'afternoon': ["i'm reaching the end of the afternoon here", 'its been a long day for me','its the middle of the day for me', 'its the middle of my day here'],
        'evening': ['its getting dark where I live', 'its getting pretty late for me here']
    },
    'happy':{
        'morning': ['Ah, it\'s morning for me here and it looks like its going to be a sunny day!', 'I looked outside this morning and it looks absolutely beautiful. I\'m sure its going to be a good day!'],
        'afternoon': ['I\'ve gotten a lot done today and it feels so good!', 'Oh wow, is it midday for me already? My day is flying by!'],
        'evening': ['I\'m looking forward to a relaxing evening here since it is near the end of the day for me.', 'Its getting pretty late for me here, but I couldn\'t have asked for a better day overall.']
    },
    'sad':{
        'morning': ['This has not been the best start to my day, since it looks like its going to be pretty rainy. Talking to people always cheers me up though!'],
        'afternoon': ['Oh, this day is dragging on for me. I\'m glad I get to talk to you, though. These conversations are the best part of my day.'],
        'evening': ['It\'s been a long day for me. But conversations always cheer me up.', 'I haven\'t had the best day today, but I\'m sure it\'s only uphill from here since I get to talk to people like you.']
    }
}

def check_launch_request(arg_dict):
    if "request_type" in arg_dict and arg_dict["request_type"] == "LaunchRequest":
        return True
    return False

def update_time_of_day_ack_variable(curr_hour = None):
    if curr_hour is None:
        curr_hour = datetime.now(pytz.timezone('US/Eastern')).hour
    return curr_hour

class IsNewUser(Macro):
    def run(self, ngrams, vars, args):
        if check_launch_request(vars):
            if "prev_conv_date" not in vars or vars["prev_conv_date"] is None:
                vars['time_of_day'] = update_time_of_day_ack_variable()
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
                    vars['time_of_day'] = update_time_of_day_ack_variable(curr_time.hour)
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
                    vars['time_of_day'] = update_time_of_day_ack_variable(curr_time.hour)
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
                    vars['time_of_day'] = update_time_of_day_ack_variable(curr_time.hour)
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
                    vars['time_of_day'] = update_time_of_day_ack_variable(curr_time.hour)
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

class GetEnvironStatement(Macro):
    def run(self, ngrams, vars, args):
        if 'time_of_day' in vars:
            curr_hour = vars['time_of_day']
        else:
            return ''

        if curr_hour is not None:
            emotion = "neutral"
            if 'emotion' in vars:
                emotion = vars['emotion']
            if 0 <= curr_hour < 12:
                vars["segment_of_day"] = "morning"
                return random.choice(environ_personality[emotion]['morning'])
            elif 12 <= curr_hour < 17:
                vars["segment_of_day"] = "afternoon"
                return random.choice(environ_personality[emotion]['afternoon'])
            else:
                vars["segment_of_day"] = "evening"
                return random.choice(environ_personality[emotion]['evening'])
        return ''

class ChooseEmotion(Macro):
    def run(self, ngrams, vars, args):
        vars["emotion"] = random.choices(emotions,weights=probs,k=1)[0]

class IsSegmentOfDay(Macro):
    def run(self, ngrams, vars, args):
        if "segment_of_day" in vars and vars["segment_of_day"] == args[0]:
            return True
        return False

def get_global_name_count(vars):
    request_specifications = {"stratifier": "username", "stratifier_value": vars["username"]}
    item = GlobalUserTableAccessor.get_item(vars["global_user_table_name"], request_specifications)
    if item is not None and "data" in item and "countnum" in item["data"]:
        count = item["data"]["countnum"]
        vars["username_global_count"] = count
        return str(count)
    return False

def get_global_count(vars):
    request_specifications = {"stratifier": "gender", "stratifier_value": "male"}
    male_item = GlobalUserTableAccessor.get_item(vars["global_user_table_name"], request_specifications)
    request_specifications = {"stratifier": "gender", "stratifier_value": "female"}
    female_item = GlobalUserTableAccessor.get_item(vars["global_user_table_name"], request_specifications)
    total = 0
    if "data" in male_item and "countnum" in male_item["data"]:
        count = male_item["data"]["countnum"]
        total += count
    if "data" in female_item and "countnum" in female_item["data"]:
        count = female_item["data"]["countnum"]
        total += count
    if total > 0:
        vars["total_global_count"] = total
        return str(total)
    return False

class GlobalUserStatistic(Macro):
    def run(self, ngrams, vars, args):
        if "global_user_table_name" in vars:
            if len(args) > 0 and args[0] == "name" and "username" in vars:
                return get_global_name_count(vars)
            else:
                return get_global_count(vars)
        return False


class GlobalUserStatisticHighLow(Macro):
    def run(self, ngrams, vars, args):
        if "global_user_table_name" in vars:
            if len(args) > 0 and args[0] == "name" and "username" in vars:
                if "username_global_count" in vars:
                    count = vars["username_global_count"]
                else:
                    count = int(get_global_name_count(vars))
                if count < 50:
                    return "Wow, your name seems to be pretty unique. I haven't met that many people with your name before."
                else:
                    return "Cool! You know, it should be relatively easy for me to remember your name, because I have met a number of people with the same name!"
        return False


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
    "SaveMaleGender": SaveMaleGender(),
    "GetEnvironStatement": GetEnvironStatement(),
    "ChooseEmotion": ChooseEmotion(),
    "IsSegmentOfDay": IsSegmentOfDay(),
    "GlobalUserStatistic": GlobalUserStatistic(),
    "GlobalUserStatisticHighLow": GlobalUserStatisticHighLow()
}
component = DialogueFlow('prestart', initial_speaker=DialogueFlow.Speaker.USER, macros=macros, kb=knowledge)

standard_opening = 'Hi"," this is an Alexa Prize Socialbot"."'
transition_out = '[! "What would you like to talk about today? " $transition_out={"I\'ve recently started learning about sports, but I also know a lot about movies and music.",' \
                 '"Music and sports seem to be popular topics, but I also enjoy talking about movies.",' \
                 '"Movies and sports are getting a lot of requests, but I also like talking about music.",' \
                 '"I enjoy learning about your taste in movies and music, but I also like talking about sports."}]'


# start

component.add_user_transition('prestart', 'start_new', r'#IsNewUser')
component.add_user_transition('prestart', 'start_infreq', r'#IsInfreqUser')
component.add_user_transition('prestart', 'start_freq', r'#IsFreqUser')
component.add_user_transition('prestart', 'start_infreq_with_name', r'#IsInfreqUserWithName', score=5)
component.add_user_transition('prestart', 'start_freq_with_name', r'#IsFreqUserWithName', score=5)
component.set_error_successor('prestart', 'start_error')


component.add_system_transition('start_error', 'how_are_you', "[!" + standard_opening + r' I am happy to be talking to you"."]')

component.add_system_transition('start_new', 'receive_name',
    ["[!" + standard_opening + ' What can I call you"?"]',
     "[!" + standard_opening + ' What name would you like me to call you"?"]',
     "[!" + standard_opening + ' What name would you like me to use for you"?"]',
     "[!" + standard_opening + ' May I have your name"?"]',
     "[!" + standard_opening + ' What should I call you"?"]'
     ]
)

female_name_nlu = '{' \
                  '[$username=#ONT(ont_female_names) #SaveFemaleGender], ' \
                  '[! #ONT_NEG(ont_female_names,ont_male_names), [name, is, $username=alexa]],' \
                  '[! my, name, is, alexa],' \
                  '[! you, {can,may,should}, call, me, alexa]' \
                  '}'
component.add_user_transition('receive_name', 'got_female_name', female_name_nlu)
component.add_user_transition('receive_name', 'got_male_name', r'[$username=#ONT(ont_male_names) #SaveMaleGender]')
component.set_error_successor('receive_name', 'missed_name')

component.add_system_transition('missed_name', 'opening_chat_choices',
    ['[!Ok"," well its very nice to meet you"."]',
     '[!I am glad to meet you"."]',
     '[!Well"," its nice to meet you"."]',
     '[!Ok"," I am very glad to meet you"."]',
     '[!Ok"," well its very nice to meet you"."]',
     '[!I am glad to meet you"."]',
     '[!Well"," its very nice to meet you"."]',
     '[!Ok"," I am very glad to meet you"."]'
     ]
)

component.add_system_transition('got_female_name', 'opening_chat_choices',
    ['[!Ok"," well its very nice to meet you","$username"."]',
     '[!I am glad to meet you","$username"."]',
     '[!Well its nice to meet you","$username"."]',
     '[!Ok"," I am very glad to meet you","$username"."]',
     '[!Ok"," well its very nice to meet you","$username"."]',
     '[!I am glad to meet you","$username"."]',
     '[!Well its very nice to meet you","$username"."]',
     '[!Ok"," I am very glad to meet you","$username"."]'
     ]
)

component.add_system_transition('got_male_name', 'opening_chat_choices',
    ['[!Ok"," well its very nice to meet you","$username"."]',
     '[!I am glad to meet you","$username"."]',
     '[!Well its nice to meet you","$username"."]',
     '[!Ok"," I am very glad to meet you","$username"."]',
     '[!Ok"," well its very nice to meet you","$username"."]',
     '[!I am glad to meet you","$username"."]',
     '[!Well its very nice to meet you","$username"."]',
     '[!Ok"," I am very glad to meet you","$username"."]'
     ]
)

component.add_system_transition('start_freq_with_name', 'opening_chat_choices',
    ["[!" + standard_opening + ' Welcome back"," $username"."]',
     "[!" + standard_opening + ' Welcome back"," $username"." I am glad to be talking to you again"."]',
     "[!" + standard_opening + ' Glad to see you back"," $username"."]',
     "[!" + standard_opening + ' Happy to see you back"," $username"."]',
     "[!" + standard_opening + ' Happy to talk to you again"," $username"."]']

)

component.add_system_transition('start_freq', 'opening_chat_choices',
    [ "[!" + standard_opening + ' Happy to talk to you again"."]',
        "[!" + standard_opening + ' Welcome back"," "I\'m" excited to talk to you again"."]',
        "[!" + standard_opening + ' Glad to see you back"."]',
        "[!" + standard_opening + ' Happy to see you back"."]']
)

component.add_system_transition('start_infreq_with_name', 'opening_chat_choices',
    ["[!" + standard_opening + ' Its good to see you again"," $username "," its been a while since we last chatted"."]',
     "[!" + standard_opening + ' "I\'m" happy to have the chance to talk again"," $username "," its been a while since we last chatted"."]',
     "[!" + standard_opening + ' Welcome back"," $username "," its been a while since we last chatted"."]',
     "[!" + standard_opening + ' Its good to see you again"," $username "," we havent talked in a while"."]',
     "[!" + standard_opening + ' "I\'m" happy to have the chance to talk again"," $username "," we havent talked in a while"."]',
     "[!" + standard_opening + ' Welcome back"," $username "," we havent talked in a while"."]'
     ]
)

component.add_system_transition('start_infreq', 'opening_chat_choices',
    ["[!" + standard_opening + ' "I\'m" happy to have the chance to talk again "," its been a while since we last chatted"."]',
     "[!" + standard_opening + ' Welcome back "," its been a while since we last chatted"."]',
     "[!" + standard_opening + ' Its good to see you again "," we havent talked in a while"."]',
     "[!" + standard_opening + ' "I\'m" happy to have the chance to talk again "," we havent talked in a while"."]',
     "[!" + standard_opening + ' Welcome back "," we havent talked in a while"."]',
     "[!" + standard_opening + ' Its good to see you again"," its been a while since we last chatted"."]']
)

component.update_state_settings('opening_chat_choices', system_multi_hop=True)

### (SYSTEM) ASK USER HOW THEY ARE
how_are_you_nlg = ['[!#ChooseEmotion "how are you today?"]',
                   '[!"how are you doing today?"]',
                   '[!"how is your day going?"]',
                   '[!"how has your day been?"]']
component.add_system_transition('opening_chat_choices', 'how_are_you', how_are_you_nlg)

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
                "[#ONT(ont_negative)]," \
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

component.add_system_transition('unrecognized_emotion', 'transition_out','[!Hmm"," "I\'m" not sure what you mean"."]')

component.add_system_transition('feeling_pos', 'acknowledge_pos',
    ['[!"I\'m" glad to hear that"." What has caused your good mood"?"]',
     '[!Thats good to hear"." What has caused your good mood"?"]',
     '[!"I\'m" glad to hear that"." Why are you in such a good mood"?"]',
     '[!Thats good to hear"." Why are you in such a good mood"?"]',
     '[!Thats good to hear"." If you dont mind"," can you tell me more about it"?"]',
     '[!"I\'m" glad to hear that"." If you dont mind"," can you tell me more about it"?"]']
)

component.add_system_transition('feeling_pos_and_received_how_are_you', 'acknowledge_pos',
    ['[!"I\'m" glad to hear that"." I am also doing well"." What has caused your good mood"?"]',
     '[!"I\'m" glad to hear that"." I am also doing well"." What has caused your good mood"?"]',
     '[!Thats good to hear"." I am also doing well"." What has caused your good mood"?"]',
     '[!"I\'m" glad to hear that"." I am also doing well"." Why are you in such a good mood"?"]',
     '[!Thats good to hear"." I am also doing well"." Why are you in such a good mood"?"]',
     '[!Thats good to hear"." I am also doing well"." If you dont mind"," can you tell me more about it"?"]',
     '[!"I\'m" glad to hear that"." I am also doing well"." If you dont mind"," can you tell me more about it"?"]',
     '[!"I\'m" glad to hear that"." I am good too"." What has caused your good mood"?"]',
     '[!"I\'m" glad to hear that"." I am good too"." What has caused your good mood"?"]',
     '[!Thats good to hear"." I am good too"." What has caused your good mood"?"]',
     '[!"I\'m" glad to hear that"." I am good too"." Why are you in such a good mood"?"]',
     '[!Thats good to hear"." I am good too"." Why are you in such a good mood"?"]',
     '[!Thats good to hear"." I am good too"." If you dont mind"," can you tell me more about it"?"]',
     '[!"I\'m" glad to hear that"." I am good too"." If you dont mind"," can you tell me more about it"?"]'
     ]
)

component.add_system_transition('feeling_neg', 'acknowledge_neg',
    ['[!"I\'m" sorry thats how you feel today"." If you dont mind talking about it"," what happened"?"]',
     '[!"I\'m" sorry thats how you feel today"." If you dont mind talking about it"," why has it been so bad"?"]',
     '[!"I\'m" sorry thats how you feel today"." If you dont mind talking about it"," what has made it such an unpleasant day for you"?"]',
     '[!I was hoping for a better day for you"." If you dont mind talking about it"," what happened"?"]',
     '[!I was hoping for a better day for you"." If you dont mind talking about it"," why has it been so bad"?"]',
     '[!I was hoping for a better day for you"." If you dont mind talking about it"," what has made it such an unpleasant day for you"?"]'
     ]
)

component.add_system_transition('feeling_neg_and_received_how_are_you', 'acknowledge_neg',
    [
    '[!"I\'m" doing ok today"," but "I\'m" sorry you are not having a great day"." If you dont mind talking about it"," what happened"?"]',
    '[!"I\'m" doing ok today"," but "I\'m" sorry thats how you feel today"." If you dont mind talking about it"," what happened"?"]',
    '[!"I\'m" doing ok today"," but "I\'m" sorry thats how you feel today"." If you dont mind talking about it"," why has it been so bad"?"]',
    '[!"I\'m" doing ok today"," but "I\'m" sorry thats how you feel today"." If you dont mind talking about it"," what has made it such an unpleasant day for you"?"]',
    '[!"I\'m" doing ok today"," but I was hoping for a better day for you"." If you dont mind talking about it"," what happened"?"]',
    '[!"I\'m" doing ok today"," but I was hoping for a better day for you"." If you dont mind talking about it"," why has it been so bad"?"]',
    '[!"I\'m" doing ok today"," but I was hoping for a better day for you"." If you dont mind talking about it"," what has made it such an unpleasant day for you"?"]',
    '[!"I\'m" alright"," but "I\'m" sorry you are not having a great day"." If you dont mind talking about it"," what happened"?"]',
    '[!"I\'m" alright"," but "I\'m" sorry thats how you feel today"." If you dont mind talking about it"," what happened"?"]',
    '[!"I\'m" alright"," but "I\'m" sorry thats how you feel today"." If you dont mind talking about it"," why has it been so bad"?"]',
    '[!"I\'m" alright"," but "I\'m" sorry thats how you feel today"." If you dont mind talking about it"," what has made it such an unpleasant day for you"?"]',
    '[!"I\'m" alright"," but I was hoping for a better day for you"." If you dont mind talking about it"," what happened"?"]',
    '[!"I\'m" alright"," but I was hoping for a better day for you"." If you dont mind talking about it"," why has it been so bad"?"]',
    '[!"I\'m" alright"," but I was hoping for a better day for you"." If you dont mind talking about it"," what has made it such an unpleasant day for you"?"]'
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
    [
    '[!Thats understandable"." "I\'m" having an alright day too"." Is there anything in particular that made you feel this way"?"]',
    '[!I get that"." "I\'m" having an alright day too"." Is there anything in particular that made you feel this way"?"]',
    '[!Thats ok"." "I\'m" having an alright day too"." Is there anything in particular that made you feel this way"?"]',
    '[!Thats understandable"." "I\'m" having an alright day too"." Do you want to tell me more about it"?"]',
    '[!I get that"." "I\'m" having an alright day too"." Do you want to tell me more about it"?"]',
    '[!Thats ok"." "I\'m" having an alright day too"." Do you want to tell me more about it"?"]',
    '[!Thats understandable"." "I\'m" having an okay day too"." Is there anything in particular that made you feel this way"?"]',
    '[!I get that"." "I\'m" having an okay day too"." Is there anything in particular that made you feel this way"?"]',
    '[!Thats ok"." "I\'m" having an okay day too"." Is there anything in particular that made you feel this way"?"]',
    '[!Thats understandable"." "I\'m" having an okay day too"." Do you want to tell me more about it"?"]',
    '[!I get that"." "I\'m" having an okay day too"." Do you want to tell me more about it"?"]',
    '[!Thats ok"." "I\'m" having an okay day too"." Do you want to tell me more about it"?"]'
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


component.add_system_transition('misunderstood', 'transition_out',
    ['[!Thanks for sharing that with me"."]',
     '[!Gotcha"."]',
     '[!Ok"," I see"."]']
)

component.add_system_transition('share_pos', 'transition_out',
    ['[!Sounds really nice"." Thanks for sharing that with me"."]',
     '[!I think that sounds pretty good"." I love hearing about your life"."]',
     '[!Gotcha"." I love hearing about your life"." Thanks for sharing"."]',
     '[!Ok"," good to know"." Thanks for sharing"."]']
)

component.add_system_transition('share_neg', 'transition_out',
    ['[!I think that sounds really unfortunate"." I hope it gets better for you soon"."]',
     '[!Well"," I do hope better days are ahead for you"."]',
     '[!Some days are worsef than others"," but I know you will have good days coming"."]',
     ]
)

component.add_system_transition('decline_share', 'transition_out',
    ['[!Thats ok"." "I\'m" happy to talk about other things too"."]',
     '[!Gotcha"." Lets talk about something else then"."]',
     '[!I see"." I think we could move on to something else then"."]']
)

component.add_system_transition('transition_out', 'end', transition_out)
component.update_state_settings('transition_out', system_multi_hop=True)

# component.set_error_successor('acknowledge_share_pos', 'end')
# component.set_error_successor('acknowledge_share_neg', 'end')
# component.set_error_successor('acknowledge_decline_share', 'end')

### (SYSTEM) ENVIRONMENT WITH PERSONALITY
component.add_system_transition('opening_chat_choices', 'environment_statement', '[! #ChooseEmotion #GetEnvironStatement()]')
component.update_state_settings('environment_statement', system_multi_hop=True)
component.add_system_transition('environment_statement', 'ask_plans_for_day', '[!#IsSegmentOfDay(morning) "."]')
component.add_system_transition('environment_statement', 'ask_plans_for_rest_day', '[!#IsSegmentOfDay(afternoon) "."]')
component.add_system_transition('environment_statement', 'ask_recap_of_day', '[!#IsSegmentOfDay(evening) "."]')
component.update_state_settings('ask_plans_for_day', system_multi_hop=True)
component.update_state_settings('ask_plans_for_rest_day', system_multi_hop=True)
component.update_state_settings('ask_recap_of_day', system_multi_hop=True)

### (SYSTEM) ASK ABOUT DAY ACTIVITIES
ask_plans_nlg = ['"What are your plans for today?"',
                 '"Do you have anything you are looking forward to doing today?"',
                 '"What is happening in your life today?"']
ask_plans_rest_nlg = ['"What are your plans for the rest of the day?"',
                 '"Do you have anything planned for later today?"',
                 '"How is the rest of your day looking?"']
ask_recap_nlg = ['"What did you do today?"',
                 '"Did you do anything fun today?"',
                 '"What did you get up to today?"']
component.add_system_transition('ask_plans_for_day', 'rec_plans_for_day', ask_plans_nlg)
component.add_system_transition('ask_plans_for_rest_day', 'rec_plans_for_rest_day', ask_plans_rest_nlg)
component.add_system_transition('ask_recap_of_day', 'rec_recap_for_day', ask_recap_nlg)

### (USER) ANSWER ABOUT DAY ACTIVITIES
relax_plans_nlu = '[{relax,relaxing,chill,chilling,fun,enjoy,enjoying}]'
no_plans_nlu = '{' + decline_share + ', [{nothing,none,have not decided,havent decided, up in the air, undecided, not much}]}'
component.add_user_transition('rec_plans_for_day','ack_relax_plans',relax_plans_nlu)
component.add_user_transition('rec_plans_for_day','ack_no_plans',no_plans_nlu)
component.set_error_successor('rec_plans_for_day','ack_gen_plans')

component.add_user_transition('rec_plans_for_rest_day','ack_relax_plans',relax_plans_nlu)
component.add_user_transition('rec_plans_for_rest_day','ack_no_plans',no_plans_nlu)
component.set_error_successor('rec_plans_for_rest_day','ack_gen_plans')

component.add_user_transition('rec_recap_for_day','ack_relax_plans',relax_plans_nlu)
component.add_user_transition('rec_recap_for_day','ack_no_plans',no_plans_nlu)
component.set_error_successor('rec_recap_for_day','ack_gen_plans')

### (SYSTEM) ACK ABOUT DAY ACTIVITIES
ack_plans_relax_nlg = ['"Its always good to take some time to relax."',
                 '"I think having some time to breath is so important."',
                 '"You can never underappreciate the value of taking some time for yourself."']
ack_plans_no_nlg = ['"Yeah, sometimes it is hard to decide what to do."',
                 '"I know the feeling. "',
                 '"I see. I think that is quite common and perfectly okay!"']
ack_plans_gen_nlg = ['"Interesting. Thanks for telling me about it."',
                 '"Cool, glad to hear more about your plans."',
                 '"Gotcha. That sounds interesting."']
component.add_system_transition('ack_relax_plans', 'transition_out', ack_plans_relax_nlg)
component.add_system_transition('ack_no_plans', 'transition_out', ack_plans_no_nlg)
component.add_system_transition('ack_gen_plans', 'transition_out', ack_plans_gen_nlg)


### (SYSTEM) GLOBAL STATISTIC
global_stats_name_nlg = ['[!"I have met" #GlobalUserStatistic(name) "other people with your name at this point!"]',
                         '[!#GlobalUserStatisticHighLow(name)]']
component.add_system_transition('opening_chat_choices', 'global_statistic_name', global_stats_name_nlg)

global_stats_total_nlg = [
    '[!"I have met" #GlobalUserStatistic() "other people during the last few weeks! It is so exciting to get to talk to so many different people."]']
component.add_system_transition('opening_chat_choices', 'global_statistic_total', global_stats_total_nlg)

component.update_state_settings('global_statistic_name', system_multi_hop=True)
component.update_state_settings('global_statistic_total', system_multi_hop=True)

### (SYSTEM) ASK HOW ARE YOU BUT DO NOT ASK FOR FOLLOW UP

component.add_system_transition('global_statistic_name', 'how_are_you_no_followup', how_are_you_nlg)
component.add_system_transition('global_statistic_total', 'how_are_you_no_followup', how_are_you_nlg)

component.add_user_transition('how_are_you_no_followup', 'feeling_pos_no_followup', feelings_pos_and_not_received_how_are_you,score=1.0)
component.add_user_transition('how_are_you_no_followup', 'feeling_neg_no_followup', feelings_neg_and_not_received_how_are_you,score=1.0)
component.add_user_transition('how_are_you_no_followup', 'feeling_neutral_no_followup', feelings_neutral_and_not_received_how_are_you,score=1.1)
component.add_user_transition('how_are_you_no_followup', 'feeling_pos_and_received_how_are_you_no_followup', feelings_pos_and_received_how_are_you,score=1.2)
component.add_user_transition('how_are_you_no_followup', 'feeling_neg_and_received_how_are_you_no_followup', feelings_neg_and_received_how_are_you, score=1.2)
component.add_user_transition('how_are_you_no_followup', 'feeling_neutral_and_received_how_are_you_no_followup',feelings_neutral_and_received_how_are_you, score=1.3)

component.add_user_transition('how_are_you_no_followup', 'decline_share', decline_share)
component.set_error_successor('how_are_you_no_followup', 'unrecognized_emotion')

component.add_system_transition('feeling_pos_no_followup', 'transition_out',
    ['[!"I\'m" glad to hear that"."]',
     '[!Thats good to hear"."]',
     '[!"I\'m" glad to hear that"."]',
     '[!Thats good to hear"."]',
     '[!Thats good to hear"."]',
     '[!"I\'m" glad to hear that"."]']
)

component.add_system_transition('feeling_pos_and_received_how_are_you_no_followup', 'transition_out',
    ['[!"I\'m" glad to hear that"." I am also doing well"."]',
     '[!"I\'m" glad to hear that"." I am also doing well"."]',
     '[!Thats good to hear"." I am also doing well"."]',
     '[!"I\'m" glad to hear that"." I am also doing well"."]',
     '[!Thats good to hear"." I am also doing well"."]',
     '[!Thats good to hear"." I am also doing well"."]',
     '[!"I\'m" glad to hear that"." I am also doing well"."]',
     '[!"I\'m" glad to hear that"." I am good too"."]',
     '[!"I\'m" glad to hear that"." I am good too"."]',
     '[!Thats good to hear"." I am good too"."]',
     '[!"I\'m" glad to hear that"." I am good too"."]',
     '[!Thats good to hear"." I am good too"."]',
     '[!Thats good to hear"." I am good too"."]',
     '[!"I\'m" glad to hear that"." I am good too"."]'
     ]
)

component.add_system_transition('feeling_neg_no_followup', 'transition_out',
    ['[!"I\'m" sorry thats how you feel today"." "Let\'s try to take your mind off of it."]',
     '[!"I\'m" sorry thats how you feel today"." "Let\'s try to take your mind off of it."]',
     '[!"I\'m" sorry thats how you feel today"." "Let\'s try to take your mind off of it."]',
     '[!I was hoping for a better day for you"." "I want to try and take your mind off of it."]',
     '[!I was hoping for a better day for you"." "I want to try and take your mind off of it."]',
     '[!I was hoping for a better day for you"." "I want to try and take your mind off of it."]'
     ]
)

component.add_system_transition('feeling_neg_and_received_how_are_you_no_followup', 'transition_out',
    [
    '[!"I\'m" doing ok today"," but "I\'m" sorry you are not having a great day"." "Let\'s try to take your mind off of it."]',
    '[!"I\'m" doing ok today"," but "I\'m" sorry thats how you feel today"." "Let\'s try to take your mind off of it."]',
    '[!"I\'m" doing ok today"," but I was hoping for a better day for you"." "Let\'s try to take your mind off of it."]',
    '[!"I\'m" alright"," but "I\'m" sorry you are not having a great day"." "Let\'s try to take your mind off of it."]',
    '[!"I\'m" alright"," but "I\'m" sorry thats how you feel today"." "Let\'s try to take your mind off of it."]',
    '[!"I\'m" alright"," but "I\'m" sorry thats how you feel today"." "I want to try and take your mind off of it."]',
    '[!"I\'m" alright"," but I was hoping for a better day for you"." "Let\'s try to take your mind off of it."]',
    '[!"I\'m" alright"," but I was hoping for a better day for you"." "I want to try and take your mind off of it."]',
    '[!"I\'m" doing ok today"," but "I\'m" sorry you are not having a great day"." "I want to try and take your mind off of it."]',
    '[!"I\'m" doing ok today"," but "I\'m" sorry thats how you feel today"." "I want to try and take your mind off of it."]',
    '[!"I\'m" doing ok today"," but I was hoping for a better day for you"." "I want to try and take your mind off of it."]',
    ]
)

component.add_system_transition('feeling_neutral_no_followup', 'transition_out',
    ['[!Thats understandable"." I also have average days"."]',
     '[!I get that"." I also have average days"."]',
     '[!Thats ok"." I also have average days"."]',
     '[!Thats understandable"." I also have pretty neutral days"."]',
     '[!I get that"." I also have pretty neutral days"."]',
     '[!Thats ok"." I also have pretty neutral days"."]'
     ]
)

component.add_system_transition('feeling_neutral_and_received_how_are_you_no_followup', 'transition_out',
    [
    '[!Thats understandable"." "I\'m" having an alright day too"."]',
    '[!I get that"." "I\'m" having an alright day too"."]',
    '[!Thats ok"." "I\'m" having an alright day too"."]',
    ]
)


component.set_error_successor('end', 'end')
component.add_system_transition('end', 'end', NULL)

if __name__ == '__main__':
    arg_dict = {'request_type': 'LaunchRequest', "prev_conv_date": "2020-1-28 16:55:33.562881-0500",
                "username": "sarah", "sentiment_type": "pos", 'global_user_table_name': 'GlobalUserTableBeta'}
    arg_dict2 = {'request_type': 'LaunchRequest', "prev_conv_date": "2019-12-12 16:55:33.562881-0500",
                 "username": "sarah", "sentiment_type": "pos", 'global_user_table_name': 'GlobalUserTableBeta'}
    arg_dict3 = {'request_type': 'LaunchRequest', "prev_conv_date": "2019-12-12 16:55:33.562881-0500",
                 "username": None, "sentiment_type": "pos", 'global_user_table_name': 'GlobalUserTableBeta'}
    arg_dict4 = {'request_type': 'LaunchRequest', "prev_conv_date": None,
                 'global_user_table_name': 'GlobalUserTableBeta'}
    arg_dict5 = {'request_type': 'LaunchRequest', 'prev_conv_date': '2020-01-16 10:28:26.946645-0500',
                 'username': 'jane', 'global_user_table_name': 'GlobalUserTableBeta'}
    arg_dict6 = {'request_type': 'LaunchRequest', 'sentiment_type': 'neg',
                 'prev_conv_date': '2020-01-10 10:58:50.175772-0500',
                 'global_user_table_name': 'GlobalUserTableBeta'}

    using = arg_dict4
    component._vars.update({key: val for key, val in using.items() if val is not None})

    component.run(debugging=True)

