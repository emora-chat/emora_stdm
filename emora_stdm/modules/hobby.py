from emora_stdm import DialogueFlow, KnowledgeBase
from enum import Enum

class State(Enum):
    ASK_HOBBY = 0
    RECOG_NO_INFO_HOBBY = 1
    ASK_FAVE_THING = 2
    EXPERIENCE = 3
    CHALLENGE = 4
    UNSURE = 5
    NO_RECOG_FAVE = 6
    NO_RECOG_HOBBY = 7
    READING_GENRE = 8

hobby_opinion = {
    "cooking",
    "programming",
    "reading",
    "running",
    "writing"
}

knowledge = KnowledgeBase()
knowledge.load_json_file("hobbies.json")
df = DialogueFlow(State.START, DialogueFlow.Speaker.USER, kb=knowledge)

init_hobby_nlu = ["[[! #ONT(also_syns)?, i, #ONT(also_syns)?, like, $like_hobby=#ONT(unknown_hobby), #ONT(also_syns)?]]",
                  "[#ONT(unknown_hobby)]"]
df.add_user_transition(State.ASK_HOBBY, State.RECOG_NO_INFO_HOBBY, init_hobby_nlu)
df.set_error_successor(State.ASK_HOBBY, State.NO_RECOG_HOBBY)

reading_genre_nlg = ['DO THIS NEXT'

                    ]

df.add_system_transition(State.NO_RECOG_HOBBY, State.READING_GENRE, reading_genre_nlg)

ask_fave_thing_nlg = ['[!You like $like_hobby"?" I dont know much about it"." What is your favorite thing about $like_hobby"?"]',
                        '[!Huh"," $like_hobby"?" Not many people that ive talked to have mentioned that one "." What would you say you enjoy the most about $like_hobby"?"]',
                        '[!You like $like_hobby"?" Ive never done it"." What is your favorite thing about $like_hobby"?"]',
                        '[!Its interesting that you said $like_hobby"." That doesnt seem to be as common as other hobbies"," at least in my conversations with others"." What do you enjoy the most about $like_hobby"?"]'
                      ]
df.add_system_transition(State.RECOG_NO_INFO_HOBBY, State.ASK_FAVE_THING, ask_fave_thing_nlg)

pos_exp_nlu = ["[#ONT(pos_experience)]"]
df.add_user_transition(State.ASK_FAVE_THING, State.EXPERIENCE, pos_exp_nlu)
challenge_exp_nlu = ["[#ONT(challenge_experience)]"]
df.add_user_transition(State.ASK_FAVE_THING, State.CHALLENGE, challenge_exp_nlu)
uncertain_expression_nlu = ["[#ONT(uncertain_expression)]"]
df.add_user_transition(State.ASK_FAVE_THING, State.UNSURE, uncertain_expression_nlu)

df.add_state(State.NO_RECOG_FAVE)
df.set_error_successor(State.ASK_FAVE_THING, State.NO_RECOG_FAVE)

ack_experience_nlg = ['[! its great to find something that you enjoy"." Are there any other activities that you enjoy as well"?"]',
                      '[! having fun experiences is important for everyone"," im glad you enjoy $like_hobby"." What else do you enjoy doing"?"]'
                      '[! sometimes just enjoying yourself is exactly what you need "." Do you have any other things you would consider to be hobbies"?"]'
                     ]
df.add_system_transition(State.EXPERIENCE, State.START, ack_experience_nlg)

ack_challenge_nlg = ['[! pursuing personal growth is an admirable trait"." it sounds like you embody this and i am impressed"." Are there any other activities that you enjoy as well"?"]',
                      '[! it always feels great to overcome a challenge"," im glad you find $like_hobby so rewarding"." Do you have any other things you would consider to be hobbies "?"]'
                      '[! i see"." i do think working hard at something is sometimes just as fun as doing more relaxing activities"." What else do you enjoy doing"?"]'
                        ]
df.add_system_transition(State.CHALLENGE, State.START, ack_challenge_nlg)

ack_unsure_nlg = ['[! i understand"." sometimes it is hard to put your reasons into words"." Are there any other activities that you enjoy too"?"]',
                      '[! ok"," well"," you dont always need to have an explicit reason for liking something "." Do you have any other hobbies "?"]'
                      '[! i see"." i do think that sometimes we just enjoy things so completely that we do not need to have a reason for it"." What else do you enjoy doing"?"]'
                        ]
df.add_system_transition(State.UNSURE, State.START, ack_unsure_nlg)

no_recog_fave_nlg = ['[!I dont think I understood all of that"," but Im glad to hear more about your opinions"." Do you have any other hobbies"?"]',
                     '[!You are so knowledgeable about $like_hobby"." I am hoping to learn all sorts of things like this"," so I am very happy to be talking to you"." Are there any other hobbies you enjoy"?"]',
                     '[!Thanks for sharing that with me"." I am very interested in learning about your opinions"." It is so much fun to see what people like"!" What other activities do you enjoy doing"?"]']

df.add_system_transition(State.NO_RECOG_FAVE, State.START, no_recog_fave_nlg) # MAYBE DONT GO BACK TO STATE.START ????




if __name__ == '__main__':
    # automatic verification of the DialogueFlow's structure (dumps warnings to stdout)
    df.check()
    # run the DialogueFlow in interactive mode to test
    df.run(debugging=False)