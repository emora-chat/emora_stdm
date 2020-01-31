from emora_stdm import DialogueFlow, KnowledgeBase
from enum import Enum, auto

class State(Enum):
    ASK_HOBBY = auto()
    REC_HOBBY = auto()
    RECOG_NO_INFO_HOBBY = auto()
    ASK_FAVE_THING = auto()
    EXPERIENCE = auto()
    CHALLENGE = auto()
    UNSURE = auto()
    NO_RECOG_FAVE = auto()
    NO_RECOG_HOBBY = auto()
    READING_GENRE = auto()

hobby_opinion = {
    "cooking",
    "programming",
    "reading",
    "running",
    "writing"
}

knowledge = KnowledgeBase()
knowledge.load_json_file("hobbies.json")
df = DialogueFlow(State.ASK_HOBBY, DialogueFlow.Speaker.USER, kb=knowledge)

### (SYSTEM) TWO OPTIONS FOR STARTING HOBBY COMPONENT - what hobby do you like vs ive heard of hobby, do you like it

ask_hobby_nlg = ['"There are so many choices of what to do these days for fun. I never know what to choose. What is your favorite hobby?"',
                 '"Im always looking for new activities to try out. Tell me, what is your favorite hobby these days?"',
                 '"Do you have an activity you like to do in your free time? I like learning new things to try out based on what other people like."',
                 '"Everyone has such different answers to this, but I was wondering what you like to do to relax and have fun? "',
                 ]
df.add_system_transition(State.ASK_HOBBY, State.REC_HOBBY, ask_hobby_nlg)



### (USER) RECEIVING SPECIFIC HOBBY USER LIKES WHERE HOBBY HAS NO INFO FOR EMORA

init_hobby_nlu = ["[[! #ONT(also_syns)?, i, #ONT(also_syns)?, like, $like_hobby=#ONT(unknown_hobby), #ONT(also_syns)?]]",
                  "[$like_hobby=#ONT(unknown_hobby)]"]
df.add_user_transition(State.REC_HOBBY, State.RECOG_NO_INFO_HOBBY, init_hobby_nlu)
df.set_error_successor(State.REC_HOBBY, State.NO_RECOG_HOBBY)

### (SYSTEM) ASKING FOR FAVORITE THING ABOUT NO INFO HOBBY

ask_fave_thing_nlg = ['[!You like $like_hobby"?" I dont know much about it"." What is your favorite thing about $like_hobby"?"]',
                        '[!Huh"," $like_hobby"?" Not many people that ive talked to have mentioned that one "." What would you say you enjoy the most about $like_hobby"?"]',
                        '[!You like $like_hobby"?" Ive never done it"." What is your favorite thing about $like_hobby"?"]',
                        '[!Its interesting that you said $like_hobby"." That doesnt seem to be as common as other hobbies"," at least in my conversations with others"." What do you enjoy the most about $like_hobby"?"]'
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

ack_experience_nlg = ['[! its great to find something that you enjoy"." Are there any other activities that you enjoy as well"?"]',
                      '[! having fun experiences is important for everyone"," im glad you enjoy $like_hobby"." What else do you enjoy doing"?"]'
                      '[! sometimes just enjoying yourself is exactly what you need "." Do you have any other things you would consider to be hobbies"?"]'
                     ]
df.add_system_transition(State.EXPERIENCE, State.ASK_HOBBY, ack_experience_nlg)

ack_challenge_nlg = ['[! pursuing personal growth is an admirable trait"." it sounds like you embody this and i am impressed"." Are there any other activities that you enjoy as well"?"]',
                      '[! it always feels great to overcome a challenge"," im glad you find $like_hobby so rewarding"." Do you have any other things you would consider to be hobbies "?"]'
                      '[! i see"." i do think working hard at something is sometimes just as fun as doing more relaxing activities"." What else do you enjoy doing"?"]'
                        ]
df.add_system_transition(State.CHALLENGE, State.ASK_HOBBY, ack_challenge_nlg)

ack_unsure_nlg = ['[! i understand"." sometimes it is hard to put your reasons into words"." Are there any other activities that you enjoy too"?"]',
                      '[! ok"," well"," you dont always need to have an explicit reason for liking something "." Do you have any other hobbies "?"]'
                      '[! i see"." i do think that sometimes we just enjoy things so completely that we do not need to have a reason for it"." What else do you enjoy doing"?"]'
                        ]
df.add_system_transition(State.UNSURE, State.ASK_HOBBY, ack_unsure_nlg)

no_recog_fave_nlg = ['[!I dont think I understood all of that"," but Im glad to hear more about your opinions"." Do you have any other hobbies"?"]',
                     '[!You are so knowledgeable about $like_hobby"." I am hoping to learn all sorts of things like this"," so I am very happy to be talking to you"." Are there any other hobbies you enjoy"?"]',
                     '[!Thanks for sharing that with me"." I am very interested in learning about your opinions"." It is so much fun to see what people like"!" What other activities do you enjoy doing"?"]']

df.add_system_transition(State.NO_RECOG_FAVE, State.ASK_HOBBY, no_recog_fave_nlg)


### (SYSTEM) PROMPTING WITH READING HOBBY THAT EMORA HAS INFORMATION FOR

reading_genre_nlg = ['DO THIS NEXT'

                    ]

df.add_system_transition(State.NO_RECOG_HOBBY, State.READING_GENRE, reading_genre_nlg)


if __name__ == '__main__':
    # automatic verification of the DialogueFlow's structure (dumps warnings to stdout)
    df.check()
    # run the DialogueFlow in interactive mode to test
    df.run(debugging=False)