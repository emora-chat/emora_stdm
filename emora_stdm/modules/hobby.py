from emora_stdm import DialogueFlow, KnowledgeBase, Macro, ONTE
from enum import Enum, auto

class IsHobby(Macro):
    def run(self, ngrams, vars, args):
        if "hobby" in vars and len(args) > 0:
            if vars["hobby"] == args[0]:
                return True
        return False

class IsNoInfoHobby(Macro):
    def __init__(self, d):
        self.onte = d._macros["ONTE"]

    def run(self, ngrams, vars, args):
        if "hobby" in vars and len(args) > 0:
            if vars["hobby"] in self.onte("unknown_hobby"):
                return True
        return False

class State(Enum):
    PRESTART = auto()
    FIRST_ASK_HOBBY = auto()
    GEN_ASK_HOBBY = auto()
    REC_HOBBY = auto()
    RECOG_NO_INFO_HOBBY = auto()
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
    LIKE_HOBBY_ERR = auto()
    ASK_GENRE = auto()
    UNRECOG_GENRE = auto()

hobby_opinion = {
    "cooking",
    "programming",
    "reading",
    "running",
    "writing"
}

knowledge = KnowledgeBase()
knowledge.load_json_file("hobbies.json")
df = DialogueFlow(State.PRESTART, DialogueFlow.Speaker.USER,
                  kb=knowledge)
macros = {"IsHobby": IsHobby(), "IsNoInfoHobby": IsNoInfoHobby(df)}
df._macros.update(macros)

### if user initiates
request_hobby_nlu = '[#EXP(chat)? {hobby,hobbies,activity,activities,fun things,things to do,pasttimes}]'
df.add_user_transition(State.PRESTART, State.FIRST_ASK_HOBBY,request_hobby_nlu)
df.set_error_successor(State.PRESTART, State.PRESTART)
df.add_system_transition(State.PRESTART, State.PRESTART, '"NULL TRANSITION"')

### (SYSTEM) TWO OPTIONS FOR STARTING HOBBY COMPONENT - what hobby do you like vs ive heard of hobby, do you like it

first_ask_hobby_nlg = ['"There are so many choices of what to do these days for fun. I never know what to choose. What is your favorite hobby?"',
                 '"Im always looking for new activities to try out. Tell me, what is your favorite hobby these days?"',
                 '"Do you have an activity you like to do in your free time? I like learning new things to try out based on what other people like."',
                 '"Everyone has such different answers to this, but I was wondering what you like to do to relax and have fun? "',
                 ]
df.add_system_transition(State.FIRST_ASK_HOBBY, State.REC_HOBBY, first_ask_hobby_nlg)

gen_ask_hobby_nlg = ['"What is another hobby you like?"',
                        '"Tell me, what is another one of your favorite hobbies?"',
                        '"Do you have a different activity you like to do in your free time?"',
                         '"What do you like to do to have fun?"',
                     '"Are there any other activities that you enjoy as well?"',
                     '"What else do you enjoy doing?"',
                     '"Do you have any other things you would consider to be hobbies?"']
df.add_system_transition(State.GEN_ASK_HOBBY, State.REC_HOBBY, gen_ask_hobby_nlg)

# todo - also need to check for untalked about hobby
first_prompt_hobby_nlg = ['[!One activity that a lot of people have mentioned to me is $hobby={#ONTN(known_hobby),#ONTN(unknown_hobby)}"." Is this something you like to do"?"]',
                    '[!Ive been hearing a bit about $hobby={#ONTN(known_hobby),#ONTN(unknown_hobby)}"." Do you like $hobby"?"]'
                    ]
df.add_system_transition(State.FIRST_ASK_HOBBY, State.PROMPT_HOBBY, first_prompt_hobby_nlg)
df.add_system_transition(State.GEN_ASK_HOBBY, State.PROMPT_HOBBY, first_prompt_hobby_nlg)

### (USER) ANSWERING YES TO PROMPT HOBBY
# todo - store talked hobby
# todo - store likes hobby
yes_nlu = '[{#EXP(yes),#ONT(yes_qualifier)}]'
df.add_user_transition(State.PROMPT_HOBBY, State.LIKE_HOBBY, yes_nlu)
df.update_state_settings(State.LIKE_HOBBY, user_multi_hop=True)
df.add_user_transition(State.LIKE_HOBBY, State.LIKE_READING, "#IsHobby(reading)")
df.add_user_transition(State.LIKE_HOBBY, State.RECOG_NO_INFO_HOBBY, "#IsNoInfoHobby")
like_hobby_err_nlg = ['"Sorry, I dont seem to have understood your answer very well. Lets try something else."',
                     '[!"Im glad you like" $hobby ". Now I am curious."]'
                     ]
df.set_error_successor(State.LIKE_HOBBY, State.LIKE_HOBBY_ERR)
df.add_system_transition(State.LIKE_HOBBY_ERR, State.GEN_ASK_HOBBY, like_hobby_err_nlg)

### (USER) ANSWERING NO TO PROMPT HOBBY
no_nlu = '{[#EXP(no)], [!{i dont, i do not, no i dont, no i do not}]}'
df.add_user_transition(State.PROMPT_HOBBY, State.ACK_NO_LIKE, '[#EXP(no)]')

### (USER) ANSWERING NEVER TRIED TO PROMPT HOBBY
never_tried_nlu = '{[! -you [never] [{tried, heard, done}]], [#ONT(uncertain_expression)]}'
df.add_user_transition(State.PROMPT_HOBBY, State.ACK_NEVER_TRIED, never_tried_nlu)

### (USER) ERROR TO PROMPT HOBBY
prompt_hobby_err_nlg = ['"Sorry, I dont seem to have understood your answer very well. Lets try something else."',
                        '[!"You have provided an interesting answer to whether you like" $hobby ", but I am still learning about it. "]'
                     ]
df.set_error_successor(State.PROMPT_HOBBY, State.PROMPT_RES_ERR)
df.add_system_transition(State.PROMPT_RES_ERR, State.GEN_ASK_HOBBY, prompt_hobby_err_nlg)

### (SYSTEM) RESPONDING TO USERS NO TO LIKE HOBBY PROMPT
# todo - store talked hobby
df.update_state_settings(State.GEN_ASK_HOBBY, system_multi_hop=True)
ack_no_like_nlg = ['[!"I see. Im glad to learn that you dont really care for" $hobby "."]',
                    '[!"Really? Thats very interesting to hear that you dont like" $hobby "."]'
                    ]
df.add_system_transition(State.ACK_NO_LIKE, State.GEN_ASK_HOBBY, ack_no_like_nlg)

### (SYSTEM) RESPONDING TO NEVER TRIED TO LIKE HOBBY PROMPT
# todo - store talked hobby
ack_never_tried_nlg = ['[!"Oh. It sounds like you have never tried" $hobby ". Thats ok."]',
                        '[!"Wow, youve never done it? I find it fascinating to see the diversity in everyones life, since others have mentioned" $hobby "to me before."]'
                        ]
df.add_system_transition(State.ACK_NEVER_TRIED, State.GEN_ASK_HOBBY, ack_never_tried_nlg)

### (USER) RECEIVING SPECIFIC HOBBY USER LIKES WHERE HOBBY HAS INFO FOR EMORA

### (USER) RECEIVING SPECIFIC HOBBY USER LIKES WHERE HOBBY HAS NO INFO FOR EMORA

init_noinfo_hobby_nlu = ["[[! #ONT(also_syns)?, i, #ONT(also_syns)?, like, $hobby=#ONT(unknown_hobby), #ONT(also_syns)?]]",
                  "[$hobby=#ONT(unknown_hobby)]"]
df.add_user_transition(State.REC_HOBBY, State.RECOG_NO_INFO_HOBBY, init_noinfo_hobby_nlu)
init_info_hobby_nlu = ["[[! #ONT(also_syns)?, i, #ONT(also_syns)?, like, $hobby=#ONT(known_hobby), #ONT(also_syns)?]]",
                        "[$hobby=#ONT(known_hobby)]"]
df.add_user_transition(State.REC_HOBBY, State.LIKE_HOBBY, init_info_hobby_nlu)
df.set_error_successor(State.REC_HOBBY, State.NO_RECOG_HOBBY)

### (SYSTEM) ACKNOWLEDING IT HAS NEVER HEARD OF SUCH HOBBY
# todo - save utterance into user attributes
no_recog_hobby_nlg = ['"Ive never heard that one. What is your favorite thing about it?"',
                        '"Im not very familiar with that. What would you say you enjoy the most about it?"',
                        '"Wow, it is not every day that I hear about a brand new activity for me. What is your favorite thing about it?"',
                        '"I dont remember if I have ever heard of that activity before. What do you enjoy the most about it?"'
                      ]
df.add_system_transition(State.NO_RECOG_HOBBY, State.ASK_FAVE_THING, no_recog_hobby_nlg)

### (SYSTEM) ASKING FOR FAVORITE THING ABOUT NO INFO HOBBY

ask_fave_thing_nlg = ['[!You like $hobby"?" I dont know much about it"." What is your favorite thing about $hobby"?"]',
                        '[!Huh"," $hobby"?" Not many people that ive talked to have mentioned that one "." What would you say you enjoy the most about $hobby"?"]',
                        '[!You like $hobby"?" Ive never done it"." What is your favorite thing about $hobby"?"]',
                        '[!Its interesting that you said $hobby"." That doesnt seem to be as common as other hobbies"," at least in my conversations with others"." What do you enjoy the most about $hobby"?"]'
                      ]
df.add_system_transition(State.RECOG_NO_INFO_HOBBY, State.ASK_FAVE_THING, ask_fave_thing_nlg)

### (USER) RECEIVING FAVORITE THING ABOUT NO INFO HOBBY

pos_exp_nlu = ["[#ONT(pos_experience)]"]
df.add_user_transition(State.ASK_FAVE_THING, State.EXPERIENCE, pos_exp_nlu)
challenge_exp_nlu = ["[#ONT(challenge_experience)]"]
df.add_user_transition(State.ASK_FAVE_THING, State.CHALLENGE, challenge_exp_nlu)
uncertain_expression_nlu = ["[#ONT(uncertain_expression)]"]
df.add_user_transition(State.ASK_FAVE_THING, State.UNSURE, uncertain_expression_nlu)

df.add_state(State.NO_RECOG_FAVE)
df.set_error_successor(State.ASK_FAVE_THING, State.NO_RECOG_FAVE)

### (SYSTEM) RESPONDING TO FAVORITE THING ABOUT NO INFO HOBBY

ack_experience_nlg = ['[! its great to find something that you enjoy"."]',
                      '[! having fun experiences is important for everyone"," im glad you enjoy $hobby"."]'
                      '[! sometimes just enjoying yourself is exactly what you need "."]'
                     ]
df.add_system_transition(State.EXPERIENCE, State.GEN_ASK_HOBBY, ack_experience_nlg)

ack_challenge_nlg = ['[! pursuing personal growth is an admirable trait"." it sounds like you embody this and i am impressed"."]',
                      '[! it always feels great to overcome a challenge"," im glad you find $hobby so rewarding"."]'
                      '[! i see"." i do think working hard at something is sometimes just as fun as doing more relaxing activities"."]'
                        ]
df.add_system_transition(State.CHALLENGE, State.GEN_ASK_HOBBY, ack_challenge_nlg)

ack_unsure_nlg = ['[! i understand"." sometimes it is hard to put your reasons into words"."]',
                      '[! ok"," well"," you dont always need to have an explicit reason for liking something "."]'
                      '[! i see"." i do think that sometimes we just enjoy things so completely that we do not need to have a reason for it"."]'
                        ]
df.add_system_transition(State.UNSURE, State.GEN_ASK_HOBBY, ack_unsure_nlg)

no_recog_fave_nlg = ['[!I dont think I understood all of that"," but Im glad to hear more about your opinions"."]',
                     '[!You are so knowledgeable about $hobby"." I am hoping to learn all sorts of things like this"," so I am very happy to be talking to you"."]',
                     '[!Thanks for sharing that with me"." I am very interested in learning about your opinions"." It is so much fun to see what people like"!"]']

df.add_system_transition(State.NO_RECOG_FAVE, State.GEN_ASK_HOBBY, no_recog_fave_nlg)


### (SYSTEM) ASKING ABOUT FAVE GENRE OF BOOK

reading_ask_genre_nlg = ['"Oh, you like reading? What kind of books do you enjoy the most?"',
                        '"Im so glad you like reading. Books are a great way to explore imaginary worlds and characters. What type of books do you like reading?"',
                         '"Reading can be so much fun. What stories do you find the most enjoyable?"'
                        ]

df.add_system_transition(State.LIKE_READING, State.ASK_GENRE, reading_ask_genre_nlg)


### (USER) SHARING FAVE GENRE OF BOOK
df.set_error_successor(State.ASK_GENRE, State.UNRECOG_GENRE)
fave_genre_error_nlg = ['"I dont know if I know of any books like that, but that is something I will think about."',
                        '"Huh, what a unique answer. Im not sure what kinds of books those are, but I am looking forward to looking into this more."'
                        ]
df.add_system_transition(State.UNRECOG_GENRE, State.GEN_ASK_HOBBY, fave_genre_error_nlg)

if __name__ == '__main__':
    # automatic verification of the DialogueFlow's structure (dumps warnings to stdout)
    df.check()
    # run the DialogueFlow in interactive mode to test
    df.run(debugging=True)