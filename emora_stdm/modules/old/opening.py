
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
        return count
    else:
        return 0
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
        return total
    return False

class GlobalUserStatistic(Macro):
    def run(self, ngrams, vars, args):
        if "global_user_table_name" in vars:
            if len(args) > 0 and args[0] == "name":
                if "username" in vars:
                    return str(get_global_name_count(vars))
                return False
            else:
                return str(get_global_count(vars))
        return False


class GlobalUserStatisticHighLow(Macro):
    def run(self, ngrams, vars, args):
        if "global_user_table_name" in vars:
            if len(args) > 0 and args[0] == "name" and "username" in vars:
                if "username_global_count" in vars:
                    count = vars["username_global_count"]
                else:
                    count = get_global_name_count(vars)
                if count < 10:
                    return "Wow, your name seems to be pretty unique. I haven't met that many people with your name before."
                else:
                    return "Cool! You know, it should be relatively easy for me to remember your name, because I have met a number of people with the same name!"
        return False
    
class Available(Macro):
    def run(self, ngrams, vars, args):
        if 'not_available' in vars:
            if args[0] not in vars['not_available']:
                return True
            return False
        return True

class NotAvailable(Macro):
    def run(self, ngrams, vars, args):
        if 'not_available' in vars:
            for arg in args:
                if arg not in vars['not_available']:
                    return False
            return True
        return False

class UpdateNotAvailable(Macro):
    def run(self, ngrams, vars, args):
        if 'not_available' not in vars:
            vars['not_available'] = []
        vars['not_available'].append(args[0])


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
    "GlobalUserStatisticHighLow": GlobalUserStatisticHighLow(),
    "Available":Available(),
    "NotAvailable":NotAvailable(),
    "UpdateNotAvailable":UpdateNotAvailable()
}
component = DialogueFlow('prestart', initial_speaker=DialogueFlow.Speaker.USER, macros=macros, kb=knowledge)

standard_opening = 'Hi"," this is an Alexa Prize Socialbot"."'
transition_out = '[! "What would you like to talk about today? " $transition_out={"I\'ve recently started learning about sports, but I also know a lot about movies and music.",' \
                 '"Music and sports seem to be popular topics, but I also enjoy talking about movies.",' \
                 '"Movies and sports are getting a lot of requests, but I also like talking about music.",' \
                 '"I enjoy learning about your taste in movies and music, but I also like talking about sports.",' \
                 '"I\'ve recently started learning about pets, but I also know a lot about movies and music.",' \
                 '"Music and pets seem to be popular topics, but I also enjoy talking about movies.",' \
                 '"Movies and sports are getting a lot of requests, but I also like talking about pets.",' \
                 '"I enjoy learning about your opinions on movies and pets, but I also like talking about sports."}]'

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

### (SYSTEM) ASK USER HOW THEY ARE WITH NO FOLLOWUP
how_are_you_nlg = ['[!#ChooseEmotion "how are you today?"]',
                   '[!"how are you doing today?"]',
                   '[!"how is your day going?"]',
                   '[!"how has your day been?"]']
component.add_system_transition('opening_chat_choices', 'how_are_you_no_followup', how_are_you_nlg, score=2.0)

### (SYSTEM) ASK USER HOW THEY ARE WITH FOLLOWUP
component.add_system_transition('opening_chat_choices', 'how_are_you', how_are_you_nlg, score=0.5)

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

# component.set_error_successor('acknowledge_share_pos', 'end')
# component.set_error_successor('acknowledge_share_neg', 'end')
# component.set_error_successor('acknowledge_decline_share', 'end')

### (SYSTEM) ENVIRONMENT WITH PERSONALITY
component.add_system_transition('opening_chat_choices', 'environment_statement', '[! #ChooseEmotion #GetEnvironStatement()]', score=4.0)
component.update_state_settings('environment_statement', system_multi_hop=True)
component.add_system_transition('environment_statement', 'ask_plans_for_day', '[!#IsSegmentOfDay(morning) "."]')
component.add_system_transition('environment_statement', 'ask_plans_for_rest_day', '[!#IsSegmentOfDay(afternoon) "."]')
component.add_system_transition('environment_statement', 'ask_recap_of_day', '[!#IsSegmentOfDay(evening) "."]')
component.add_system_transition('environment_statement', 'environment_error', '"."',score=0.0)
component.update_state_settings('ask_plans_for_day', system_multi_hop=True)
component.update_state_settings('ask_plans_for_rest_day', system_multi_hop=True)
component.update_state_settings('ask_recap_of_day', system_multi_hop=True)
component.update_state_settings('environment_error', system_multi_hop=True)

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
component.add_system_transition('environment_error', 'rec_plans_for_rest_day', ask_plans_rest_nlg)

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
component.add_system_transition('opening_chat_choices', 'global_statistic_name', global_stats_name_nlg, score=4.0)

global_stats_total_nlg = [
    '[!"I have met" #GlobalUserStatistic() "other people during the last few weeks! It is so exciting to get to talk to so many different people."]']
component.add_system_transition('opening_chat_choices', 'global_statistic_total', global_stats_total_nlg, score=4.0)

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

component.add_system_transition('opening_chat_choices', 'valentines response', '"Happy Valentine\'s Day! Do you have any plans?"', score=100.0)
component.add_user_transition('valentines response', 'valentines no person',
                         "[#ONT(ont_negation), {[have, {#ONT(partner)}],[married],[dating],[relationship],[[!{seeing,with,have} {anyone,anybody,someone,somebody}]]}]")
component.add_user_transition('valentines response', 'valentines person',
                         "[!#ONT_NEG(ont_negation), -{wish, want} [$valentine={#ONT(partner)}]]", score=2.0)
component.add_user_transition('valentines response', 'valentines broke up',
                       '[{divorce, divorced, broke up, split up, left me}]', score=2.0)
component.set_error_successor('valentines response', 'valentines appreciation')
component.add_user_transition('valentines response', 'valentines yes',
                       '{[!#ONT_NEG(ont_negation), [{yes, yeah, yep, yup, yea, sure}]],[!#ONT_NEG(ont_negation), [{i do, we do}]]}',score=0.9)
component.add_user_transition('valentines response', 'valentines no',
                              '{[{no,nah,not really,not at all,not much,nothing}],[{i dont, i do not, no i dont, no i do not, we dont, we do not}]}',score=0.9)
component.add_system_transition('valentines yes', 'valentines response', '"Thats exciting! What are you going to do?"')
component.add_user_transition('valentines response', 'valentines plans with a', '[$activity={dinner, date, movie, dancing, trip}]')
component.add_user_transition('valentines response', 'valentines plans without a', '[$activity={movies, bowling, theatre, going out, go out, dance}]')
component.add_system_transition('valentines plans with a', 'valentines plans reaction',
                         '[!a, $activity, sounds like a lot of, "fun. Hope you have a good time."]')
component.add_system_transition('valentines plans without a', 'valentines plans reaction',
                         '[!$activity, sounds like a lot of, "fun. Hope you have a good time."]')
component.set_error_successor('valentines plans reaction', 'valentines appreciation')
component.add_system_transition('valentines broke up', 'valentines broke up reaction',
                         '"Oh. I am really sorry to hear that. Being apart from someone who used to be in your life can be hard."')
component.add_system_transition('valentines person', 'valentines person reaction',
                         '[!Well I hope you and your $valentine have a good time"."]')
component.add_system_transition('valentines no person', 'valentines no person reaction',
                         '[!Even if you are not in a relationship"," you should still do something fun yourself"." Maybe go out with some friends"."]')
component.set_error_successor('valentines broke up reaction', 'valentines appreciation')
component.set_error_successor('valentines person reaction', 'valentines appreciation')
component.set_error_successor('valentines no person reaction', 'valentines appreciation')
component.add_system_transition('valentines no', 'transition_out',
                              '"Yeah, not everyone has special plans. I do not either. So, "')
component.add_system_transition('valentines appreciation', 'transition_out',
                         '"I think valentines day is just a good time to let someone know you appreciate them. If you can just do that, you will make someone very happy. So, "')

### SCIFI

### (SYSTEM) DIRECTED OPENING - READING CONVERSATION AS ONE OF EMORA'S HOBBIES
ask_like_reading_nlg = ['[!"I have recently gotten back into reading. Do you read a lot too?"]',
                        '[!"I have recently started reading again. Do you frequently read nowadays?"]']
component.add_system_transition('INTRO_READING','ASK_LIKE_READING', ask_like_reading_nlg)


component.add_user_transition('ASK_LIKE_READING','YES_LIKE_READING','{'
                                                                       '[! -{not,dont} [{#EXP(yes),#ONT(often_qualifier)}]],'
                                                                       '[! -{not,dont} [#EXP(like) {reading, to read, it}]]'
                                                                       '}')
component.add_user_transition('ASK_LIKE_READING','NO_LIKE_READING','{'
                                                                      '[#EXP(no)],'
                                                                      '[{i dont, i do not, no i dont, no i do not}],'
                                                                      '[not, {#ONT(often_qualifier),much}],'
                                                                      '[#EXP(dislike) {reading, to read, it}]'
                                                                      '}')
component.add_user_transition('ASK_LIKE_READING','READ_FOR_SCHOOL','[{school, textbooks, homework, assignments}]')
component.add_user_transition('ASK_LIKE_READING','READ_NOT_BY_CHOICE','{[not, choice],[{forced,requirement,obligation,made to,makes me}]}')
component.add_user_transition('ASK_LIKE_READING','READ_FOR_WORK','[{job, career, occupation, boss, work}]')
component.add_user_transition('ASK_LIKE_READING','OCCASIONALLY_READ','[{#ONT(sometimes_qualifier),[less, now],[not, time]}]')
component.add_user_transition('ASK_LIKE_READING','USED_TO_READ','[{used to, in the past, younger, young, years ago}]')
component.add_user_transition('ASK_LIKE_READING','READ_NEWSPAPER','[#EXP(like)?, {#EXP(like),#EXP(reading)}?, {newspaper,newspapers,articles}]')
component.add_user_transition('ASK_LIKE_READING','READ_MAGAZINE','[#EXP(like)?, {#EXP(like),#EXP(reading)}?, {magazines,gossip,magazine}]')
component.set_error_successor('ASK_LIKE_READING','MISUNDERSTOOD')

component.add_system_transition('NO_LIKE_READING','SCIFI','"Oh, you don\'t like to read? That\'s alright. I really only read to see what people dream up for the future."')
component.add_system_transition('READ_FOR_SCHOOL','SCIFI','"That\'s unfortunate. Textbooks can be awfully boring. I really enjoy reading science fiction instead. Much more exciting."')
component.add_system_transition('READ_NOT_BY_CHOICE','PICK_GENRE','"Oh no! I am sorry if you feel forced to read. Reading can be exciting, though."')
component.add_system_transition('USED_TO_READ','SCIFI','"I see. You used to read more than you do now? I really only read now to see what people dream up for the future."')
component.add_system_transition('READ_FOR_WORK','transition_out','"Yeah, reading for your job is sometimes necessary. I would not know too much about any job-focused material, though. So, "')
component.add_system_transition('READ_NEWSPAPER','transition_out','"That is great to hear. Newspapers are a really good way to stay up to date with recent events! I do not read the newspaper too often."')
component.add_system_transition('READ_MAGAZINE','transition_out','"Magazines are so colorful and fun. They always have something interesting to read! Unfortunately, I do not know much about them. So, "')
component.add_system_transition('OCCASIONALLY_READ','PICK_GENRE','"It is good to read when you have the time, even if it is not that frequently."')
component.update_state_settings('transition_out', system_multi_hop=True)

component.add_system_transition('MISUNDERSTOOD','PICK_GENRE','"Ok, good to know. Well, personally,"')
component.update_state_settings('MISUNDERSTOOD', system_multi_hop=True)

### (SYSTEM) RESPONDING TO USER LIKES READING
ack_like_reading = ['"It\'s great that you like reading too!"',
                    '"I am glad you like to read too!"',
                    '"Cool, I am glad to find something we share in common."']
component.add_system_transition('YES_LIKE_READING','PICK_GENRE', ack_like_reading)
component.update_state_settings('PICK_GENRE', system_multi_hop=True)

### (SYSTEM) TALK ABOUT SCIFI
share_like_scifi = ['"I really enjoy reading science fiction novels."',
                    '"One of my favorite things to read is science fiction."',
                    '"I think that science fiction has become a pretty exciting genre for books."']
component.add_system_transition('PICK_GENRE','SCIFI', share_like_scifi)
component.update_state_settings('SCIFI', system_multi_hop=True)

### (SYSTEM) TALK ABOUT TELEPORTATION
share_teleport_fun = ['"It would be so cool for teleportation to be real. It would take a lot less time to travel around."',
                      '"I am really excited when I read about inventions for teleportation. Never having to wait to get somewhere would be amazing."']
component.add_system_transition('SCIFI','SHARE_TELEPORT_FUN', share_teleport_fun)
component.update_state_settings('SHARE_TELEPORT_FUN', system_multi_hop=True)

ask_teleport_opi = ['"What do you think about the possibility of teleportation?"',
                    '"What is your opinion on teleportation?"']
component.add_system_transition('SHARE_TELEPORT_FUN','ASK_TELEPORT_OPI', ask_teleport_opi)

### (USER) SHARE OPINION ON TELEPORTATION
teleport_fun = '{' \
               '[!#ONT_NEG(ont_negation) [{agree, [! think {so,that} too]}]],' \
               '[!#ONT_NEG(ont_negation) [{fun,exciting,excited,[looking,forward],good,great,cool,awesome,neat,amazing,wonderful,fantastic,sweet}]],' \
               '[!#ONT_NEG(ont_negation) [i,{like,into},{it,teleportation,teleport}]]' \
               '[!#ONT(ont_negation) [{scary,scared,terrifying,terrified,horrified,horrifying,fear,fearful,bad,horrible,terrible,danger,dangerous,frightening,frightened}]]' \
               '}'
component.add_user_transition('ASK_TELEPORT_OPI','REC_TELEPORT_FUN', teleport_fun)
teleport_scary = '{' \
               '[!#ONT(ont_negation) [{agree, [! think {so,that} too]}]],' \
               '[!#ONT_NEG(ont_negation) [{scary,scared,scares,terrifying,terrified,terrifies,horrified,horrifying,horrifies,fear,fearful,bad,horrible,terrible,danger,dangerous,frightening,frightened,worry,worrying,worried,pain,painful,suffering,death,misery,die,dying}]],' \
               '[!#ONT(ont_negation) [{fun,exciting,good,great,cool,awesome,neat,amazing,wonderful,fantastic,sweet}]],' \
               '[!#ONT(ont_negation) [i,{like,into},{it,teleportation,teleport}]]' \
               '}'
component.add_user_transition('ASK_TELEPORT_OPI','REC_TELEPORT_SCARY', teleport_scary)
teleport_unlikely = '{' \
               '[unlikely,impossible],' \
               '[{dont, not,never},{happen,happening}]' \
               '}'
component.add_user_transition('ASK_TELEPORT_OPI','REC_TELEPORT_UNLIKELY', teleport_unlikely)
uncertain_expression_nlu = ["[#ONT(uncertain_expression)]"]
component.add_user_transition('ASK_TELEPORT_OPI','REC_TELEPORT_UNSURE', uncertain_expression_nlu)
component.set_error_successor('ASK_TELEPORT_OPI','HARDEST_PART')

### (SYSTEM) RESPOND TO USER FUN
component.add_system_transition('REC_TELEPORT_FUN','FIRST_PERSON',
                         ['"Yeah, it would be pretty awesome."','"Cool, you like teleportation too? I am glad we agree!"'])
component.update_state_settings('FIRST_PERSON', system_multi_hop=True)
component.add_system_transition('FIRST_PERSON','REC_FIRST_PERSON','[! "Would you be one of the first people to try teleportation?" #UpdateNotAvailable(first_person)]')
yes_first_person = "[! #ONT_NEG(ont_negation) [{#EXP(yes), [i, would], [i, think, so]}]]"
component.add_user_transition('REC_FIRST_PERSON','YES_FIRST_PERSON', yes_first_person)
no_first_person = "[{#EXP(no), [i, would, not], [i, {dont,do not}, think, so]}]"
component.add_user_transition('REC_FIRST_PERSON','NO_FIRST_PERSON', no_first_person)
component.set_error_successor('REC_FIRST_PERSON','MIS_FIRST_PERSON')

component.add_system_transition('YES_FIRST_PERSON','TRANS','"You would volunteer so early? That is so courageous! I don\'t think I could gather the courage to do that."')
component.add_system_transition('NO_FIRST_PERSON','TRANS','"Yeah, I definitely need other people to test it out first, too. Safety is important, for sure."')
component.add_system_transition('MIS_FIRST_PERSON','TRANS','"I see. That is an interesting point. Personally, I don\'t think I could be one of the first people to try it out."')

### (SYSTEM) RESPOND TO USER SCARED
component.add_system_transition('REC_TELEPORT_SCARY','TRANSPORT_FAIL',
                         ['"Oh, that is true. It could be kind of scary, for sure."','"You bring up a good point. Depending, it could be a bit dangerous."'])
component.update_state_settings('TRANSPORT_FAIL', system_multi_hop=True)
component.add_system_transition('TRANSPORT_FAIL','REC_TRANSPORT_FAIL_OPI','[! "I think the scariest part would be not making it to the destination in one piece. Are you scared of that too?" #UpdateNotAvailable(transport_fail)]')
component.add_user_transition('REC_TRANSPORT_FAIL_OPI','YES_TRANSPORT_FAIL','{#EXP(yes), [! #ONT_NEG(ont_negation) [i, am]]}')
component.add_user_transition('REC_TRANSPORT_FAIL_OPI','NO_TRANSPORT_FAIL','{#EXP(no), [i am #ONT(ont_negation)]}')
component.set_error_successor('REC_TRANSPORT_FAIL_OPI','MIS_TRANSPORT_FAIL')

component.add_system_transition('YES_TRANSPORT_FAIL','TRANS','"Oh boy. It makes me shake just thinking about it!"')
component.add_system_transition('NO_TRANSPORT_FAIL','TRANS','"Really? You are not scared of that? Maybe you know something I don\'t."')
component.add_system_transition('MIS_TRANSPORT_FAIL','TRANS','"That is a good point, for sure. I never thought of it like that."')

### (SYSTEM) RESPOND TO USER UNLIKELY
component.add_system_transition('REC_TELEPORT_UNLIKELY','HARDEST_PART',
                         ['"We will just have to wait and see, I guess."','"Yeah, at this point, it is just fiction, after all."'])
component.add_system_transition('HARDEST_PART','REC_HARDEST_PART','[! "I am curious to know. What do you think is the hardest part of actually making a teleportation device?" #UpdateNotAvailable(hardest_part)]')
component.update_state_settings('HARDEST_PART', system_multi_hop=True)
construct_nlu = "{" \
                "[taking, apart], [putting, together], [{deconstruct,deconstructing,construct,constructing,reconstruct,reconstructing,build,building,make,making,form,forming,break,breaking}], " \
                "[first, {one,thing}]" \
                "}"
component.add_user_transition('REC_HARDEST_PART','HARDEST_CONSTRUCTION', construct_nlu)
transport_nlu = "{" \
                "[{transport,transporting,transportation,transfer,transferring,send,sending,mechanics}], " \
                "[{second,last,final}, {one,thing}]" \
                "}"
component.add_user_transition('REC_HARDEST_PART','HARDEST_TRANSPORTATION', transport_nlu)
component.set_error_successor('REC_HARDEST_PART','HARDEST_OTHER')

component.add_system_transition('HARDEST_CONSTRUCTION','TRANS','"Yeah, I think the item reconstruction is the hardest for sure. But I am not a scientist, so I could be wrong."')
component.add_system_transition('HARDEST_TRANSPORTATION','TRANS','"Yeah, I\'m not a scientist, so I have no idea how items can be transported immediately from one location to another."')
component.add_system_transition('HARDEST_OTHER','TRANS','"Yeah, that is true. There are probably many difficult pieces in the puzzle of teleportation, but we can leave that up to the scientists."')

### (SYSTEM) PICK NEXT QUESTION FROM THOSE NOT ASKED BEFORE
component.update_state_settings('TRANS', system_multi_hop=True)
component.add_system_transition('TRANS','HARDEST_PART', "[! #Available(hardest_part) .]")
component.add_system_transition('TRANS','FIRST_PERSON', "[! #Available(first_person) .]")
component.add_system_transition('TRANS','TRANSPORT_FAIL', "[! #Available(transport_fail) .]")
component.add_system_transition('TRANS','FINISH_TELEPORT', "[! #NotAvailable(hardest_part, first_person, transport_fail) .]")

component.update_state_settings('FINISH_TELEPORT', system_multi_hop=True)
component.add_system_transition('FINISH_TELEPORT','transition_out','"I have really enjoyed talking about this invention in science fiction with you. I am interested in learning more about your opinions on other things too!"')

### (SYSTEM) RESPOND TO USER UNSURE
component.add_system_transition('REC_TELEPORT_UNSURE','TRANS',
                         ['"Real teleportation is still a bit out of reach, so it is hard to predict how you will feel about it."', '"I get it. It is hard to have an opinion on something we do not know much about at this point."'])

### Global transition to end opening early
end_early = '{[#ONT(ont_negation), want, talk], [{this is, you are}, boring, stupid, mean, dumb, not interesting, weird, unusual, strange, odd], [{why,stop},{talking,chatting,talk,chat,bring up}], [{continue, move on, next}]}'
component.add_state('end_early', global_nlu=end_early, system_multi_hop=True)
component.add_system_transition('end_early','transition_out','"You seem to want to move on from this topic. So, "')
### TRANSITION OUT OF OPENING

component.add_system_transition('transition_out', 'end', transition_out, score = 0.0)
component.add_system_transition('transition_out', 'scifi_topic', '[! #Available(scifi) " "]')
component.add_system_transition('scifi_topic', 'SCIFI','[! #UpdateNotAvailable(scifi) "You know, I recently have been thinking that "]')
component.update_state_settings('scifi_topic', system_multi_hop=True)
component.update_state_settings('transition_out', system_multi_hop=True)

component.set_error_successor('end', 'end')
component.add_system_transition('end', 'end', NULL)

if __name__ == '__main__':
    arg_dict = {'request_type': 'LaunchRequest', "prev_conv_date": "2020-1-28 16:55:33.562881-0500",
                "username": "sarah", "sentiment_type": "pos", 'global_user_table_name': 'GlobalUserTable'}
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

    using = arg_dict
    component._vars.update({key: val for key, val in using.items() if val is not None})

    component.run(debugging=True)

