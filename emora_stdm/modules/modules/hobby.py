from emora_stdm import DialogueFlow, KnowledgeBase, Macro, EnumByName
from enum import Enum, auto
import random, os

TRANSITION_OUT = ["movies", "music", "sports"]
NULL = "NULL TRANSITION"

class IsHobby(Macro):
    def run(self, ngrams, vars, args):
        if "hobby" in vars and len(args) > 0:
            if vars["hobby"] == args[0]:
                return True
        return False

class CheckHobbyType(Macro):
    def __init__(self, d):
        self.onte = d._macros["ONTE"]

    def run(self, ngrams, vars, args):
        if "hobby" in vars:
            type = args[0]
            if vars["hobby"] in self.onte(None, vars, [type]):
                return True
        return False

class TryGetHobby(Macro):
    def run(self, ngrams, vars, args):
        if "hobby" in vars and vars["hobby"] is not None:
            return vars["hobby"]
        else:
            return "it"

class ResetHobby(Macro):
    def run(self, ngrams, vars, args):
        if "hobby" in vars:
            vars["hobby"] = None

class ResetLoop(Macro):
    def run(self, ngrams, vars, args):
        if "loop_count" in vars:
            vars["loop_count"] = 0

class UpdateCoveredHobbies(Macro):
    def run(self, ngrams, vars, args):
        if "covered_hobbies" not in vars:
            vars["covered_hobbies"] = set()
        if len(args) == 0:
            if "hobby" in vars and vars["hobby"] is not None:
                vars["covered_hobbies"].add(vars["hobby"])
        else:
            vars["covered_hobbies"].add(args[0])
        return None

class UpdateLikedHobbies(Macro):
    def run(self, ngrams, vars, args):
        if "liked_hobbies" not in vars:
            vars["liked_hobbies"] = set()
        if "hobby" in vars and vars["hobby"] is not None:
            liked = vars["hobby"]
            vars["liked_hobbies"].add(liked)
            if "covered_hobbies" not in vars:
                vars["covered_hobbies"] = set()
            if liked not in vars["covered_hobbies"]:
                vars["covered_hobbies"].add(liked)
        return None

class UnCoveredHobby(Macro):
    def __init__(self, d):
        self.ontn = d._macros["ONTN"]
    def run(self, ngrams, vars, args):
        hobbies = self.ontn(None, vars, ["known_hobby"])
        if "covered_hobbies" in vars:
            covered = vars["covered_hobbies"]
            uncovered = hobbies - covered
            if len(uncovered) > 0:
                return uncovered
            # hobbies = self.ontn(None, vars, ["known_hobby"])
            # uncovered = hobbies - covered
            # if len(uncovered) > 0:
            #     return uncovered
            hobbies = self.ontn(None, vars, ["unknown_hobby"])
            uncovered = hobbies - covered
            if len(uncovered) > 0:
                return uncovered
            else:
                return set()
        return hobbies

class CoveredHobbySent(Macro):
    def run(self, ngrams, vars, args):
        num = int(args[0])
        if "liked_hobbies" in vars:
            hobs = random.sample(vars["liked_hobbies"], num)
            return ', and '.join(hobs)
        return 'different hobbies'

class CheckGE(Macro):
    def run(self, ngrams, vars, args):
        var = args[0]
        val = args[1]
        if val.isdigit():
            val = int(val)
        if var in vars and vars[var] >= val:
            return True
        return False

class CheckLT(Macro):
    def run(self, ngrams, vars, args):
        var = args[0]
        val = args[1]
        if val.isdigit():
            val = int(val)
        if var not in vars:
            return True
        if var in vars and vars[var] < val:
            return True
        return False

class Increment(Macro):
    def run(self, ngrams, vars, args):
        var = args[0]
        if var not in vars or vars[var] is None:
            vars[var] = 0
        vars[var] += 1
        return None

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

hobby_opinion = {
    "cooking": ["Its always so fun to try new recipes.",
                "I think the best part about cooking is getting to eat the food afterwards.",
                "There are so many recipes to choose from. It is hard to get bored of cooking, I think."],
    "programming": ["Once you know how to program, you can pretty much make your computer do anything. So powerful.",
                    "It is exciting to see what new things you can make once you start programming."],
    "running": ["Getting exercise is so important. Its good you think of it as a hobby.",
                "Running is a great way to clear your mind."],
    "writing": ["I think creating stories from your imagination is really awesome.",
                "Sometimes it can be hard to think of what to write next, but writing is a great creative outlet."],
    "biking": ["One of the best parts of biking is being able to feel like you are going so fast.",
               "Its great you bike for fun. Its a pretty good form of exercise too.",
               "I think biking is great if it lets you see beautiful nature around you."],
    "pottery": ["Pottery really lets you mold new creations with your hands.",
                "Its great to see a new object that you made come to life right before your very eyes."],
    "pool": ["My friends like to play pool with their families.",
             "I think you need good coordination to be good at pool."],
    "board games": ["Board games are a great way to bring the whole family together and have a good time.",
                    "There are so many board games already, but it also seems like new board games are always coming out. Its amazing!"],
    "bowling": ["Bowling may look easy, but it takes a lot of practice to get those strikes!",
                "Bowling is a great friendly competition to do with your friends."],
    "dance": ["There are so many forms of dance and they are all so cool!",
              "Dance is such a great activity because its so fun but also pretty healthy since you are getting a good work out in!"]
}

class GetOpinion(Macro):
    def run(self, ngrams, vars, args):
        if "hobby" in vars and vars["hobby"] in hobby_opinion:
            return random.choice(hobby_opinion[vars["hobby"]])
        return ''

class State(EnumByName):
    START = auto()
    FIRST_ASK_HOBBY = auto()
    GEN_ASK_HOBBY = auto()
    REC_HOBBY = auto()
    RECOG_NO_INFO_HOBBY = auto()
    ACK_HOBBY = auto()
    ASK_FAVE_THING = auto()
    EXPERIENCE = auto()
    CHALLENGE = auto()
    UNSURE = auto()
    NO_RECOG_FAVE = auto()
    NO_RECOG_HOBBY = auto()
    PROMPT_HOBBY = auto()
    READING_GENRE = auto()
    LIKE_READING = auto()
    ACK_NO_LIKE = auto()
    ACK_NEVER_TRIED = auto()
    PROMPT_RES_ERR = auto()
    LIKE_HOBBY = auto()
    SHARE_OPINION = auto()
    LIKE_HOBBY_ERR = auto()
    ASK_GENRE = auto()
    UNRECOG_GENRE = auto()
    CHECK_LOOP = auto()
    REDIRECT = auto()
    CONTINUE = auto()
    ACK_END = auto()
    END = auto()
    TRANSITION_OUT = auto()
    MISUNDERSTOOD = auto()

    INTRO = auto()
    INTRO_READING = auto()
    ASK_LIKE_READING = auto()
    YES_LIKE_READING = auto()
    NO_LIKE_READING = auto()
    READ_FOR_SCHOOL = auto()
    READ_NOT_BY_CHOICE = auto()
    READ_FOR_WORK = auto()
    OCCASIONALLY_READ = auto()
    USED_TO_READ = auto()
    READ_NEWSPAPER = auto()
    READ_MAGAZINE = auto()
    CONFIRM_CONTINUE = auto()
    PICK_GENRE = auto()
    SCIFI = auto()
    SHARE_TELEPORT_FUN = auto()
    ASK_TELEPORT_OPI = auto()
    REC_TELEPORT_SCARY = auto()
    REC_TELEPORT_FUN = auto()
    REC_TELEPORT_UNLIKELY = auto()
    REC_TELEPORT_UNSURE = auto()
    TRANSPORT_FAIL = auto()
    REC_TRANSPORT_FAIL_OPI = auto()
    YES_TRANSPORT_FAIL = auto()
    NO_TRANSPORT_FAIL = auto()
    MIS_TRANSPORT_FAIL = auto()
    HARDEST_PART = auto()
    REC_HARDEST_PART = auto()
    HARDEST_CONSTRUCTION = auto()
    HARDEST_TRANSPORTATION = auto()
    HARDEST_OTHER = auto()
    FIRST_PERSON = auto()
    REC_FIRST_PERSON = auto()
    YES_FIRST_PERSON = auto()
    NO_FIRST_PERSON = auto()
    MIS_FIRST_PERSON = auto()
    TRANS = auto()
    FINISH_TELEPORT = auto()
    TRANS_TO_ALIENS = auto()
    SHARE_ALIENS_SCARY = auto()
    ASK_ALIENS_SCARY = auto()
    REC_ALIENS_SCARY = auto()
    REC_ALIENS_NOT_SCARY = auto()
    REC_ALIENS_UNSURE = auto()
    ANS_WHY_ALIENS_SCARY = auto()

knowledge = KnowledgeBase()
knowledge.load_json_file(os.path.join('modules',"hobbies.json"))
df = DialogueFlow(State.START, DialogueFlow.Speaker.USER,
                  kb=knowledge)
macros = {"IsHobby": IsHobby(), "CheckHobbyType": CheckHobbyType(df),
          "UpdateCoveredHobbies": UpdateCoveredHobbies(), "UpdateLikedHobbies": UpdateLikedHobbies(),
          "TryGetHobby": TryGetHobby(), "ResetHobby": ResetHobby(), "UnCoveredHobby": UnCoveredHobby(df),
          "CoveredHobbySent": CoveredHobbySent(), "CheckGE":CheckGE(), "Increment":Increment(), "ResetLoop":ResetLoop(),
          "CheckLT":CheckLT(),"GetOpinion":GetOpinion(), "Available":Available(), "NotAvailable":NotAvailable(),
          "UpdateNotAvailable":UpdateNotAvailable()}
df._macros.update(macros)

### if user initiates
request_hobby_nlu = '[#EXP(chat)? {hobby,hobbies,activity,activities,fun things,things to do,pasttimes}]'
#df.add_user_transition(State.START, State.INTRO, request_hobby_nlu)
df.add_user_transition(State.START, State.INTRO_READING, "[{reading,read,book,books}]")
df.set_error_successor(State.START, State.START)
df.add_system_transition(State.START, State.START, NULL)

open_hobby_nlg = ['"So, it seems like you want to talk about some activities."',
                 '"So, I think you want to talk about some hobbies."',
                 '"I see. Lets talk about hobbies then."'
                 ]
df.add_system_transition(State.INTRO, State.INTRO_READING, open_hobby_nlg)
df.update_state_settings(State.INTRO_READING, system_multi_hop=True)

### (SYSTEM) DIRECTED OPENING - READING CONVERSATION AS ONE OF EMORA'S HOBBIES
ask_like_reading_nlg = ['[!"I have recently gotten back into" $hobby=reading ". Do you read a lot too?" #UpdateCoveredHobbies(reading)]',
                        '[!"I have recently started reading again. Do you frequently read nowadays?"]']
df.add_system_transition(State.INTRO_READING, State.ASK_LIKE_READING, ask_like_reading_nlg)


df.add_user_transition(State.ASK_LIKE_READING, State.YES_LIKE_READING, '{'
                                                                       '[! -{not,dont} [{#EXP(yes),#ONT(often_qualifier)}]],'
                                                                       '[! -{not,dont} [#EXP(like) {reading, to read, it}]]'
                                                                       '}')
df.add_user_transition(State.ASK_LIKE_READING, State.NO_LIKE_READING, '{'
                                                                      '[#EXP(no)],'
                                                                      '[{i dont, i do not, no i dont, no i do not}],'
                                                                      '[not, {#ONT(often_qualifier),much}],'
                                                                      '[#EXP(dislike) {reading, to read, it}]'
                                                                      '}')
df.add_user_transition(State.ASK_LIKE_READING, State.READ_FOR_SCHOOL, '[{school, textbooks, homework, assignments}]')
df.add_user_transition(State.ASK_LIKE_READING, State.READ_NOT_BY_CHOICE, '{[not, choice],[{forced,requirement,obligation,made to,makes me}]}')
df.add_user_transition(State.ASK_LIKE_READING, State.READ_FOR_WORK, '[{job, career, occupation, boss, work}]')
df.add_user_transition(State.ASK_LIKE_READING, State.OCCASIONALLY_READ, '[{#ONT(sometimes_qualifier),[less, now],[not, time]}]')
df.add_user_transition(State.ASK_LIKE_READING, State.USED_TO_READ, '[{used to, in the past, younger, young, years ago}]')
df.add_user_transition(State.ASK_LIKE_READING, State.READ_NEWSPAPER, '[#EXP(like)?, {#EXP(like),#EXP(reading)}?, {newspaper,newspapers,articles}]')
df.add_user_transition(State.ASK_LIKE_READING, State.READ_MAGAZINE, '[#EXP(like)?, {#EXP(like),#EXP(reading)}?, {magazines,gossip,magazine}]')
df.set_error_successor(State.ASK_LIKE_READING, State.MISUNDERSTOOD)

df.add_system_transition(State.NO_LIKE_READING, State.SCIFI, '"Oh, you don\'t like to read? That\'s alright. I really only read to see what people dream up for the future."')
df.add_system_transition(State.READ_FOR_SCHOOL, State.SCIFI, '"That\'s unfortunate. Textbooks can be awfully boring. I really enjoy reading science fiction instead. Much more exciting."')
df.add_system_transition(State.READ_NOT_BY_CHOICE, State.PICK_GENRE, '"Oh no! I am sorry if you feel forced to read. Reading can be exciting, though."')
df.add_system_transition(State.USED_TO_READ, State.SCIFI, '"I see. You used to read more than you do now? I really only read now to see what people dream up for the future."')
df.add_system_transition(State.READ_FOR_WORK, State.TRANSITION_OUT, '"Yeah, reading for your job is sometimes necessary. I would not know too much about any job-focused material, though. So, "')
df.add_system_transition(State.READ_NEWSPAPER, State.TRANSITION_OUT, '"That is great to hear. Newspapers are a really good way to stay up to date with recent events! I do not read the newspaper too often."')
df.add_system_transition(State.READ_MAGAZINE, State.TRANSITION_OUT, '"Magazines are so colorful and fun. They always have something interesting to read! Unfortunately, I do not know much about them. So, "')
df.add_system_transition(State.OCCASIONALLY_READ, State.PICK_GENRE, '"It is good to read when you have the time, even if it is not that frequently."')
df.update_state_settings(State.TRANSITION_OUT, system_multi_hop=True)


df.add_system_transition(State.MISUNDERSTOOD, State.PICK_GENRE, '"Ok, good to know. Well, personally,"')
df.update_state_settings(State.MISUNDERSTOOD, system_multi_hop=True)
#df.add_system_transition(State.TRANSITION_OUT, State.END, '"What would you like to chat about next? I think %s would be good."'%(', or '.join(TRANSITION_OUT)))

### (SYSTEM) RESPONDING TO USER LIKES READING
ack_like_reading = ['"It\'s great that you like reading too!"',
                    '"I am glad you like to read too!"',
                    '"Cool, I am glad to find something we share in common."']
df.add_system_transition(State.YES_LIKE_READING, State.PICK_GENRE, ack_like_reading)
df.update_state_settings(State.PICK_GENRE, system_multi_hop=True)

### (SYSTEM) TALK ABOUT SCIFI
share_like_scifi = ['"I really enjoy reading science fiction novels."',
                    '"One of my favorite things to read is science fiction."',
                    '"I think that science fiction has become a pretty exciting genre for books."']
df.add_system_transition(State.PICK_GENRE, State.SCIFI, share_like_scifi)
df.update_state_settings(State.SCIFI, system_multi_hop=True)

### (SYSTEM) TALK ABOUT TELEPORTATION
share_teleport_fun = ['"It would be so cool for teleportation to be real. It would take a lot less time to travel around."',
                      '"I am really excited when I read about inventions for teleportation. Never having to wait to get somewhere would be amazing."']
df.add_system_transition(State.SCIFI, State.SHARE_TELEPORT_FUN, share_teleport_fun)
df.update_state_settings(State.SHARE_TELEPORT_FUN, system_multi_hop=True)

ask_teleport_opi = ['"What do you think about the possibility of teleportation?"',
                    '"What is your opinion on teleportation?"']
df.add_system_transition(State.SHARE_TELEPORT_FUN, State.ASK_TELEPORT_OPI, ask_teleport_opi)

### (USER) SHARE OPINION ON TELEPORTATION
teleport_fun = '{' \
               '[!#ONT_NEG(ont_negation) [{agree, [! think {so,that} too]}]],' \
               '[!#ONT_NEG(ont_negation) [{fun,exciting,excited,[looking,forward],good,great,cool,awesome,neat,amazing,wonderful,fantastic,sweet}]],' \
               '[!#ONT_NEG(ont_negation) [i,{like,into},{it,teleportation,teleport}]]' \
               '[!#ONT(ont_negation) [{scary,scared,terrifying,terrified,horrified,horrifying,fear,fearful,bad,horrible,terrible,danger,dangerous,frightening,frightened,frightens}]]' \
               '}'
df.add_user_transition(State.ASK_TELEPORT_OPI, State.REC_TELEPORT_FUN, teleport_fun)
teleport_scary = '{' \
               '[!#ONT(ont_negation) [{agree, [! think {so,that} too]}]],' \
               '[!#ONT_NEG(ont_negation) [{scary,scared,scares,terrifying,terrified,terrifies,horrified,horrifying,horrifies,fear,fearful,bad,horrible,terrible,danger,dangerous,frightening,frightened,frightens,worry,worrying,worried,pain,painful,suffering,death,misery,die,dying}]],' \
               '[!#ONT(ont_negation) [{fun,exciting,good,great,cool,awesome,neat,amazing,wonderful,fantastic,sweet}]],' \
               '[!#ONT(ont_negation) [i,{like,into},{it,teleportation,teleport}]]' \
               '}'
df.add_user_transition(State.ASK_TELEPORT_OPI, State.REC_TELEPORT_SCARY, teleport_scary)
teleport_unlikely = '{' \
               '[unlikely,impossible],' \
               '[{dont, not,never},{happen,happening}]' \
               '}'
df.add_user_transition(State.ASK_TELEPORT_OPI, State.REC_TELEPORT_UNLIKELY, teleport_unlikely)
uncertain_expression_nlu = ["[#ONT(uncertain_expression)]"]
df.add_user_transition(State.ASK_TELEPORT_OPI, State.REC_TELEPORT_UNSURE, uncertain_expression_nlu)
df.set_error_successor(State.ASK_TELEPORT_OPI, State.HARDEST_PART)

### (SYSTEM) RESPOND TO USER FUN
df.add_system_transition(State.REC_TELEPORT_FUN, State.FIRST_PERSON,
                         ['"Yeah, it would be pretty awesome."', '"Cool, you like teleportation too? I am glad we agree!"'])
df.update_state_settings(State.FIRST_PERSON, system_multi_hop=True)
df.add_system_transition(State.FIRST_PERSON, State.REC_FIRST_PERSON, '[! "Would you be one of the first people to try teleportation?" #UpdateNotAvailable(first_person)]')
yes_first_person = "[! #ONT_NEG(ont_negation) [{#EXP(yes), [i, would], [i, think, so]}]]"
df.add_user_transition(State.REC_FIRST_PERSON, State.YES_FIRST_PERSON, yes_first_person)
no_first_person = "[{#EXP(no), [i, would, not], [i, {dont,do not}, think, so]}]"
df.add_user_transition(State.REC_FIRST_PERSON, State.NO_FIRST_PERSON, no_first_person)
df.set_error_successor(State.REC_FIRST_PERSON, State.MIS_FIRST_PERSON)

df.add_system_transition(State.YES_FIRST_PERSON, State.TRANS, '"You would volunteer so early? That is so courageous! I don\'t think I could gather the courage to do that."')
df.add_system_transition(State.NO_FIRST_PERSON, State.TRANS, '"Yeah, I definitely need other people to test it out first, too. Safety is important, for sure."')
df.add_system_transition(State.MIS_FIRST_PERSON, State.TRANS, '"I see. That is an interesting point. Personally, I don\'t think I could be one of the first people to try it out."')

### (SYSTEM) RESPOND TO USER SCARED
df.add_system_transition(State.REC_TELEPORT_SCARY, State.TRANSPORT_FAIL,
                         ['"Oh, that is true. It could be kind of scary, for sure."', '"You bring up a good point. Depending, it could be a bit dangerous."'])
df.update_state_settings(State.TRANSPORT_FAIL, system_multi_hop=True)
df.add_system_transition(State.TRANSPORT_FAIL, State.REC_TRANSPORT_FAIL_OPI, '[! "I think the scariest part would be not making it to the destination in one piece. Are you scared of that too?" #UpdateNotAvailable(transport_fail)]')
df.add_user_transition(State.REC_TRANSPORT_FAIL_OPI, State.YES_TRANSPORT_FAIL, '{#EXP(yes), [! #ONT_NEG(ont_negation) [i, am]]}')
df.add_user_transition(State.REC_TRANSPORT_FAIL_OPI, State.NO_TRANSPORT_FAIL, '{#EXP(no), [i am #ONT(ont_negation)]}')
df.set_error_successor(State.REC_TRANSPORT_FAIL_OPI, State.MIS_TRANSPORT_FAIL)

df.add_system_transition(State.YES_TRANSPORT_FAIL, State.TRANS, '"Oh boy. It makes me shake just thinking about it!"')
df.add_system_transition(State.NO_TRANSPORT_FAIL, State.TRANS, '"Really? You are not scared of that? Maybe you know something I don\'t."')
df.add_system_transition(State.MIS_TRANSPORT_FAIL, State.TRANS, '"That is a good point, for sure. I never thought of it like that."')

### (SYSTEM) RESPOND TO USER UNLIKELY
df.add_system_transition(State.REC_TELEPORT_UNLIKELY, State.HARDEST_PART,
                         ['"We will just have to wait and see, I guess."', '"Yeah, at this point, it is just fiction, after all."'])
df.add_system_transition(State.HARDEST_PART, State.REC_HARDEST_PART, '[! "I am curious to know. What do you think is the hardest part of actually making a teleportation device?" #UpdateNotAvailable(hardest_part)]')
df.update_state_settings(State.HARDEST_PART, system_multi_hop=True)
construct_nlu = "{" \
                "[taking, apart], [putting, together], [{deconstruct,deconstructing,construct,constructing,reconstruct,reconstructing,build,building,make,making,form,forming,break,breaking}], " \
                "[first, {one,thing}]" \
                "}"
df.add_user_transition(State.REC_HARDEST_PART, State.HARDEST_CONSTRUCTION, construct_nlu)
transport_nlu = "{" \
                "[{transport,transporting,transportation,transfer,transferring,send,sending,mechanics}], " \
                "[{second,last,final}, {one,thing}]" \
                "}"
df.add_user_transition(State.REC_HARDEST_PART, State.HARDEST_TRANSPORTATION, transport_nlu)
df.set_error_successor(State.REC_HARDEST_PART, State.HARDEST_OTHER)

df.add_system_transition(State.HARDEST_CONSTRUCTION, State.TRANS, '"Yeah, I think the item reconstruction is the hardest for sure. But I am not a scientist, so I could be wrong."')
df.add_system_transition(State.HARDEST_TRANSPORTATION, State.TRANS, '"Yeah, I\'m not a scientist, so I have no idea how items can be transported immediately from one location to another."')
df.add_system_transition(State.HARDEST_OTHER, State.TRANS, '"Yeah, that is true. There are probably many difficult pieces in the puzzle of teleportation, but we can leave that up to the scientists."')

### (SYSTEM) PICK NEXT QUESTION FROM THOSE NOT ASKED BEFORE
df.update_state_settings(State.TRANS, system_multi_hop=True, memory=0)
df.add_system_transition(State.TRANS, State.HARDEST_PART, "[! #Available(hardest_part) .]")
df.add_system_transition(State.TRANS, State.FIRST_PERSON, "[! #Available(first_person) .]")
df.add_system_transition(State.TRANS, State.TRANSPORT_FAIL, "[! #Available(transport_fail) .]")
df.add_system_transition(State.TRANS, State.FINISH_TELEPORT, "[! #NotAvailable(hardest_part, first_person, transport_fail) .]")

df.update_state_settings(State.FINISH_TELEPORT, system_multi_hop=True)
df.add_system_transition(State.FINISH_TELEPORT, State.TRANSITION_OUT, '" "')
#df.add_system_transition(State.FINISH_TELEPORT, State.TRANSITION_OUT, '"I have really enjoyed talking about this invention in science fiction with you. I am interested in learning more about your opinions on other things too!"')

### (SYSTEM) RESPOND TO USER UNSURE
df.add_system_transition(State.REC_TELEPORT_UNSURE, State.TRANS,
                         ['"Real teleportation is still a bit out of reach, so it is hard to predict how you will feel about it."', '"I get it. It is hard to have an opinion on something we do not know much about at this point."'])

### (SYSTEM) INTRODUCE ALIENS TOPIC
df.add_state(State.TRANS_TO_ALIENS)
df.update_state_settings(State.TRANS_TO_ALIENS, system_multi_hop=True)
df.add_system_transition(State.TRANS_TO_ALIENS, State.SHARE_ALIENS_SCARY,
                         ['"You know what else? I think aliens are really scary."',
                          '"Speaking of which, I also find the idea of aliens quite terrifying."'])
df.update_state_settings(State.SHARE_ALIENS_SCARY, system_multi_hop=True)

df.add_system_transition(State.SHARE_ALIENS_SCARY, State.ASK_ALIENS_SCARY,
                         ['"Do you find aliens scary too?"',
                          '"Are you scared by the prospect of aliens being real?"'])

### (USER) INTRODUCE ALIENS TOPIC
#df.add_user_transition(State.ASK_ALIENS_SCARY, State.REC_ALIENS_SCARY, )
################################################################################################################################
################################################################################################################################
################################################################################################################################
################################################################################################################################
################################################################################################################################

df.add_user_transition(State.START, State.FIRST_ASK_HOBBY, request_hobby_nlu)
### (SYSTEM) TWO OPTIONS FOR UNDIRECTED HOBBY OPENING - what hobby do you like vs ive heard of hobby, do you like it

first_ask_hobby_nlg = ['"So, it seems like you want to talk about some activities. There are so many choices of what to do these days for fun. I never know what to choose. What is one of your hobbies?"',
                 '"I see. It seems like you want to talk about different pasttimes. I\'m always looking for new activities to try out. Tell me, what activity do you enjoy doing these days?"',
                 '"So, I think you want to talk about some hobbies. Do you have an activity you like to do in your free time? I like learning new things to try out based on what other people like."',
                 '"I see. Lets talk about hobbies then. Everyone has such different answers to this, but I was wondering what you like to do to relax and have fun? "',
                 ]
df.add_system_transition(State.FIRST_ASK_HOBBY, State.REC_HOBBY, first_ask_hobby_nlg)

gen_ask_hobby_nlg = ['[!"What is another hobby you like?" #Increment(loop_count)]',
                        '[!"Tell me, what is another one of your favorite hobbies?"]',
                        '[!"Do you have a different activity you like to do in your free time?"]',
                         '[!"What do you like to do to have fun?"]',
                     '[!"Are there any other activities that you enjoy as well?"]',
                     '[!"What else do you enjoy doing?"]',
                     '[!"Do you have any other things that you would consider to be your hobbies?"]']
df.add_system_transition(State.GEN_ASK_HOBBY, State.REC_HOBBY, gen_ask_hobby_nlg)

first_prompt_hobby_nlg = ['[!So"," it seems like you want to talk about some activities" " One activity that a lot of people have mentioned to me is $hobby=#UnCoveredHobby()" " Is this something you like to do"?"]',
                    '[!I see" " It seems like you want to talk about hobbies" " Ive been hearing a bit about $hobby" " Do you like $hobby"?"]'
                    ]
gen_prompt_hobby_nlg = ['[!"Another activity that a lot of people have mentioned to me is " $hobby=#UnCoveredHobby() ". Is this something you like to do?" #Increment(loop_count)]',
                    '[!"You know, I have also been hearing a bit about " $hobby ". Do you like " $hobby "?"]'
                    ]
df.add_system_transition(State.FIRST_ASK_HOBBY, State.PROMPT_HOBBY, first_prompt_hobby_nlg)
df.add_system_transition(State.GEN_ASK_HOBBY, State.PROMPT_HOBBY, gen_prompt_hobby_nlg)

df.add_system_transition(State.CHECK_LOOP, State.GEN_ASK_HOBBY, '[!#CheckLT(loop_count,3) " "]')
redirect_nlg = ['[!#CheckGE(loop_count,3) "We seem to have been talking about hobbies for a bit. Do you want to talk about something else?"]',
                '[!#CheckGE(loop_count,3) "I am really enjoying talking to you about all of these different activities, but if you want to be done, we can move on to something else. Do you want to stop talking about hobbies?"]']
df.add_system_transition(State.CHECK_LOOP, State.REDIRECT, redirect_nlg)
df.update_state_settings(State.CHECK_LOOP, system_multi_hop=True, memory=0)
df.update_state_settings(State.REDIRECT, system_mutli_hop=True)

### (USER) ANSWERING REDIRECTION QUESTION
talk_something_else_nlu = '[! [{talk,chat,conversation,discussion,discuss,move on}] -{hobbies,activities,pasttimes,hobby,activity,pasttime}]'
df.add_user_transition(State.REDIRECT, State.ACK_END, '[! {[#EXP(yes)],%s} #ResetLoop()]'%talk_something_else_nlu)

no_nlu = '{[#EXP(no)], [{i dont, i do not, no i dont, no i do not}]}'
continue_nlu = '[{keep {talking,going}, continue, not {done,finished,completed}}]'
df.add_user_transition(State.REDIRECT, State.CONTINUE, '[! {%s,%s} #ResetLoop()]'%(continue_nlu,no_nlu))

### (SYSTEM) CONTINUING
df.add_system_transition(State.CONTINUE, State.GEN_ASK_HOBBY, ['"ok, so, let\'s see."', '"ok, let us continue then."'])

### (USER) ANSWERING YES TO PROMPT HOBBY
yes_nlu = '[! -{not,dont} [{#EXP(yes),#ONT(yes_qualifier),#EXP(like)}]]'
df.add_user_transition(State.PROMPT_HOBBY, State.LIKE_HOBBY, yes_nlu)
df.update_state_settings(State.LIKE_HOBBY, user_multi_hop=True)
df.add_user_transition(State.LIKE_HOBBY, State.LIKE_READING, "[!#IsHobby(reading)]")
df.add_user_transition(State.LIKE_HOBBY, State.ACK_HOBBY, "[!#CheckHobbyType(unknown_hobby)]")
df.add_user_transition(State.LIKE_HOBBY, State.SHARE_OPINION, "[!#CheckHobbyType(known_hobby)]")
df.add_system_transition(State.SHARE_OPINION, State.ACK_HOBBY, "[!#GetOpinion()]")
like_hobby_err_nlg = ['"Sorry, I dont seem to have understood your answer very well. Lets try something else."',
                     '[!"I\'m glad you like" #TryGetHobby() ". Now I am curious."]'
                     ]
df.set_error_successor(State.LIKE_HOBBY, State.RECOG_NO_INFO_HOBBY)

### (USER) ANSWERING NO TO PROMPT HOBBY
no_to_prompt_nlu = '{%s,[#EXP(dislike)],[{not,dont} #EXP(like)]}'%no_nlu
df.add_user_transition(State.PROMPT_HOBBY, State.ACK_NO_LIKE, no_to_prompt_nlu)

### (USER) ANSWERING NEVER TRIED TO PROMPT HOBBY
never_tried_nlu = '{[! -you [never] [{tried, heard, done}]], [#ONT(uncertain_expression)]}'
df.add_user_transition(State.PROMPT_HOBBY, State.ACK_NEVER_TRIED, never_tried_nlu)

### (USER) ERROR TO PROMPT HOBBY
prompt_hobby_err_nlg = ['[!"Sorry, I dont seem to have understood your answer very well. Lets try something else." #UpdateCoveredHobbies()]',
                        '[!"You have provided an interesting answer to whether you like" #TryGetHobby() ", but I am still learning about it. "]'
                     ]
df.set_error_successor(State.PROMPT_HOBBY, State.PROMPT_RES_ERR)
df.add_system_transition(State.PROMPT_RES_ERR, State.CHECK_LOOP, prompt_hobby_err_nlg)

### (SYSTEM) RESPONDING TO USERS NO TO LIKE HOBBY PROMPT
df.update_state_settings(State.GEN_ASK_HOBBY, system_multi_hop=True)
ack_no_like_nlg = ['[!"I see. I\'m always glad to learn more about what you dont like." #UpdateCoveredHobbies()]',
                    '[!"Really? Thats very interesting to hear that you dont like" #TryGetHobby() " "]'
                    ]
df.add_system_transition(State.ACK_NO_LIKE, State.CHECK_LOOP, ack_no_like_nlg)

### (SYSTEM) RESPONDING TO NEVER TRIED TO LIKE HOBBY PROMPT
ack_never_tried_nlg = ['[!"Oh. It sounds like you have never tried" #TryGetHobby() ". Thats ok." #UpdateCoveredHobbies()]',
                        '[!"Wow, youve never done it? I find it fascinating to see the diversity in everyones life, since others have mentioned" $hobby "to me before."]'
                        ]
df.add_system_transition(State.ACK_NEVER_TRIED, State.CHECK_LOOP, ack_never_tried_nlg)

### (USER) RECEIVING SPECIFIC HOBBY USER LIKES WHERE HOBBY HAS NO INFO FOR EMORA

init_noinfo_hobby_nlu = ["[[! #ONT(also_syns)?, i, #ONT(also_syns)?, like, $hobby=#ONT(unknown_hobby), #ONT(also_syns)?]]",
                  "[$hobby=#ONT(unknown_hobby)]"]
df.add_user_transition(State.REC_HOBBY, State.RECOG_NO_INFO_HOBBY, init_noinfo_hobby_nlu)
init_info_hobby_nlu = ["[[! #ONT(also_syns)?, i, #ONT(also_syns)?, like, $hobby=#ONT(known_hobby,deep_hobby), #ONT(also_syns)?]]",
                        "[$hobby=#ONT(known_hobby,deep_hobby)]"]
df.add_user_transition(State.REC_HOBBY, State.LIKE_HOBBY, init_info_hobby_nlu)
decline_share = "{" \
                "[#ONT(ont_negation), {talk, talking, discuss, discussing, share, sharing, tell, telling, say, saying, remember}]," \
                "<{dont,do not}, {know, want to, [have, {idea,answer,response,any,anything,one}]}>," \
                "<not, sure>" \
                "}"
no_more_hobbies_nlu = '{["no more"], [i, dont, have, more], [i, do, not, have, more], ' \
                      '[thats it], [that is it], [nothing], [all done], [im, done], [i, am, done], %s, %s}'%(no_nlu,decline_share)
df.add_user_transition(State.REC_HOBBY, State.ACK_END, no_more_hobbies_nlu)
df.set_error_successor(State.REC_HOBBY, State.NO_RECOG_HOBBY)

### (SYSTEM) END CONVO AFTER USER INDICATES NO MORE HOBBIES
end_nlg = ['[!"It has been fun talking about these different activities with you. But lets move on to something else. %s are on my mind. Which would you like to talk about?" #ResetLoop]'%(', and '.join(TRANSITION_OUT)),
            '[!"I have enjoyed learning about your opinions on different hobbies. Right now, I am also interested in %s. What topic do you want to talk about next?"]'%(', and '.join(TRANSITION_OUT)),
           '[!"This has been great. Ive learned some new things and some new activities I may end up trying. But until then, what would you like to chat about next? I think %s would be good."]'%(', or '.join(TRANSITION_OUT))
            ]
df.add_system_transition(State.ACK_END, State.END, end_nlg)
df.add_user_transition(State.END, State.FIRST_ASK_HOBBY, request_hobby_nlu),
df.add_user_transition(State.END, State.PICK_GENRE, "[{reading,read,book,books}]")
df.set_error_successor(State.END, State.END)
df.add_system_transition(State.END, State.END, NULL)

### (SYSTEM) ACKNOWLEDGING IT HAS NEVER HEARD OF SUCH HOBBY
# todo - save utterance into user attributes
no_recog_hobby_nlg = ['[!"Ive never heard that one. What is your favorite thing about it?" #ResetHobby]',
                        '[!"I\'m not very familiar with that. What would you say you enjoy the most about it?"]',
                        '[!"Wow, it is not every day that I hear about a brand new activity for me. What is your favorite thing about it?"]',
                        '[!"I dont remember if I have ever heard of that activity before. What do you enjoy the most about it?"]'
                      ]
df.add_system_transition(State.NO_RECOG_HOBBY, State.ASK_FAVE_THING, no_recog_hobby_nlg)

### (SYSTEM)ACKNOWLEDGING NO INFO HOBBY
ack_no_info_nlg = ['[!"You like " $hobby "? I dont know much about it."]',
                        '[!"Wow, you do like " $hobby "? I\'m interested in learning more about it."]',
                        '[!"Ive never done" $hobby " "]',
                        '[!"I\'m glad to learn more about the activities that you like."]'
                      ]
df.add_system_transition(State.RECOG_NO_INFO_HOBBY, State.ACK_HOBBY, ack_no_info_nlg)
df.update_state_settings(State.ACK_HOBBY, system_multi_hop=True)

### (SYSTEM) ASKING FOR FAVORITE THING

ask_fave_thing_nlg = ['[!"What is your favorite thing about" $hobby "?" #UpdateLikedHobbies()]',
                        '[!"What would you say you enjoy the most about" $hobby "?"]',
                        '[!"What do you enjoy the most about" $hobby "?"]'
                      ]
df.add_system_transition(State.ACK_HOBBY, State.ASK_FAVE_THING, ask_fave_thing_nlg)

### (USER) RECEIVING FAVORITE THING ABOUT NO INFO HOBBY

pos_exp_nlu = ["[#ONT(pos_experience)]"]
df.add_user_transition(State.ASK_FAVE_THING, State.EXPERIENCE, pos_exp_nlu)
challenge_exp_nlu = ["[#ONT(challenge_experience)]"]
df.add_user_transition(State.ASK_FAVE_THING, State.CHALLENGE, challenge_exp_nlu)
df.add_user_transition(State.ASK_FAVE_THING, State.UNSURE, uncertain_expression_nlu)

df.add_state(State.NO_RECOG_FAVE)
df.set_error_successor(State.ASK_FAVE_THING, State.NO_RECOG_FAVE)

### (SYSTEM) RESPONDING TO FAVORITE THING ABOUT NO INFO HOBBY

ack_experience_nlg = ['[! its great to find something that you enjoy" "]',
                      '[! having fun experiences is important for everyone"," "i\'m" glad you enjoy #TryGetHobby() " "]'
                      '[! sometimes just enjoying yourself is exactly what you need " "]'
                     ]
df.add_system_transition(State.EXPERIENCE, State.CHECK_LOOP, ack_experience_nlg)

ack_challenge_nlg = ['[! pursuing personal growth is an admirable trait" " it sounds like you embody this and i am impressed" "]',
                      '[! it always feels great to overcome a challenge"," "i\'m" glad you find #TryGetHobby() so rewarding" "]'
                      '[! i see" " i do think working hard at something is sometimes just as fun as doing more relaxing activities" "]'
                        ]
df.add_system_transition(State.CHALLENGE, State.CHECK_LOOP, ack_challenge_nlg)

ack_unsure_nlg = ['[! i understand" " sometimes it is hard to put your reasons into words" "]',
                      '[! ok"," well"," you dont always need to have an explicit reason for liking something " "]'
                      '[! i see" " i do think that sometimes we just enjoy things so completely that we do not need to have a reason for it" "]'
                        ]
df.add_system_transition(State.UNSURE, State.CHECK_LOOP, ack_unsure_nlg)

no_recog_fave_nlg = ['[!I dont think I understood all of that"," but "I\'m" glad to hear more about your opinions" "]',
                     '[!You are so knowledgeable about #TryGetHobby()" " I am hoping to learn all sorts of things like this"," so I am very happy to be talking to you" "]',
                     '[!Thanks for sharing that with me" " I am very interested in learning about your opinions" " It is so much fun to see what people like"!"]']

df.add_system_transition(State.NO_RECOG_FAVE, State.CHECK_LOOP, no_recog_fave_nlg)


### (SYSTEM) ASKING ABOUT FAVE GENRE OF BOOK

reading_ask_genre_nlg = ['[!"Oh, you like reading? What kind of books do you enjoy the most?" #UpdateLikedHobbies()]',
                        '[!"I\'m so glad you like reading. Books are a great way to explore imaginary worlds and characters. What type of books do you like reading?"]',
                         '[!"Reading can be so much fun. What stories do you find the most enjoyable?"]'
                        ]

df.add_system_transition(State.LIKE_READING, State.ASK_GENRE, reading_ask_genre_nlg)


### (USER) SHARING FAVE GENRE OF BOOK
df.set_error_successor(State.ASK_GENRE, State.UNRECOG_GENRE)
fave_genre_error_nlg = ['"I dont know if I know of any books like that, but that is something I will think about."',
                        '"Huh, what a unique answer. I\'m not sure what kinds of books those are, but I am looking forward to looking into this more."'
                        ]
df.add_system_transition(State.UNRECOG_GENRE, State.CHECK_LOOP, fave_genre_error_nlg)

if __name__ == '__main__':
    # automatic verification of the DialogueFlow's structure (dumps warnings to stdout)
    df.check()
    # run the DialogueFlow in interactive mode to test
    df.run(debugging=True)