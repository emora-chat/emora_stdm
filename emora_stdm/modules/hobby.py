from emora_stdm import DialogueFlow, KnowledgeBase, Macro
from enum import Enum, auto

class CheckPromptHobby(Macro):
    def run(self, ngrams, vars, args):
        if "prompt_hobby" in vars and len(args) > 0:
            if vars["prompt_hobby"] == args[0]:
                return True
        return False

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
    PROMPT_HOBBY = auto()
    READING_GENRE = auto()
    LIKE_READING = auto()
    ACK_NO_LIKE = auto()
    ACK_NEVER_TRIED = auto()
    PROMPT_RES_ERR = auto()
    LIKE_HOBBY = auto()
    LIKE_HOBBY_ERR = auto()

hobby_opinion = {
    "cooking",
    "programming",
    "reading",
    "running",
    "writing"
}

knowledge = KnowledgeBase()
knowledge.load_json_file("hobbies.json")
df = DialogueFlow(State.ASK_HOBBY, DialogueFlow.Speaker.SYSTEM, macros={"CheckPromptHobby": CheckPromptHobby()}, kb=knowledge)

### (SYSTEM) TWO OPTIONS FOR STARTING HOBBY COMPONENT - what hobby do you like vs ive heard of hobby, do you like it

ask_hobby_nlg = ['"There are so many choices of what to do these days for fun. I never know what to choose. What is your favorite hobby?"',
                 '"Im always looking for new activities to try out. Tell me, what is your favorite hobby these days?"',
                 '"Do you have an activity you like to do in your free time? I like learning new things to try out based on what other people like."',
                 '"Everyone has such different answers to this, but I was wondering what you like to do to relax and have fun? "',
                 ]
#df.add_system_transition(State.ASK_HOBBY, State.REC_HOBBY, ask_hobby_nlg)

# also need to check for untalked about hobby
prompt_hobby_nlg = ['[!One activity that a lot of people have mentioned to me is $prompt_hobby=#ONT(known_hobby)"." Is this something you like to do"?"]',
                    '[!Ive been hearing a bit about $prompt_hobby=#ONT(known_hobby)"." Do you like $prompt_hobby"?"]'
                    ]
df.add_system_transition(State.ASK_HOBBY, State.PROMPT_HOBBY, prompt_hobby_nlg)

### (USER) ANSWERING YES TO PROMPT HOBBY
# store talked about hobby
yes_nlu = '{yes,#ONT(yes_qualifier)}'
df.add_user_transition(State.PROMPT_HOBBY, State.LIKE_HOBBY, yes_nlu)
df.update_state_settings(State.LIKE_HOBBY, user_multi_hop=True)
df.add_user_transition(State.LIKE_HOBBY, State.LIKE_READING, "#CheckPromptHobby(reading)")

like_hobby_err_nlg = ['"Sorry, I dont seem to have understood your answer very well. Lets try something else."',
                     '"Im glad you like" $prompt_hobby ". Now I am curious.'
                     ]
df.set_error_successor(State.LIKE_HOBBY, State.LIKE_HOBBY_ERR)
df.add_system_transition(State.LIKE_HOBBY_ERR, State.ASK_HOBBY, like_hobby_err_nlg)

### (USER) ANSWERING NO TO PROMPT HOBBY
df.add_user_transition(State.PROMPT_HOBBY, State.ACK_NO_LIKE, '[no]')

### (USER) ANSWERING NEVER TRIED TO PROMPT HOBBY
never_tried_nlu = '{[! -you [never] [{tried, heard, done}]], [#ONT(uncertain_expression)]}'
df.add_user_transition(State.PROMPT_HOBBY, State.ACK_NEVER_TRIED, never_tried_nlu)

### (USER) ERROR TO PROMPT HOBBY
prompt_hobby_err_nlg = ['"Sorry, I dont seem to have understood your answer very well. Lets try something else."',
                     '"You have provided an interesting answer to whether you like " $prompt_hobby ". Let me see.'
                     ]
df.set_error_successor(State.PROMPT_HOBBY, State.PROMPT_RES_ERR)
df.add_system_transition(State.PROMPT_RES_ERR, State.ASK_HOBBY, prompt_hobby_err_nlg)

### (SYSTEM) RESPONDING TO NO TO LIKE HOBBY PROMPT
# store talked about hobby
df.update_state_settings(State.ASK_HOBBY, system_multi_hop=True)
ack_no_like_nlg = ['[! "I see. Im glad to learn that you dont really care for" $prompt_hobby "."]',
                    '[! "Really? Thats very interesting to hear that you dont like" $prompt_hobby "." ]'
                    ]
df.add_system_transition(State.ACK_NO_LIKE, State.ASK_HOBBY, ack_no_like_nlg)

### (SYSTEM) RESPONDING TO NEVER TRIED TO LIKE HOBBY PROMPT
# store talked about hobby
ack_never_tried_nlg = ['[! "Oh. It sounds like you have never tried" $prompt_hobby ". Thats ok."]',
                        '[! "Wow, really? I find it fascinating to see the diversity in everyones life, since others have mentioned" $prompt_hobby "to me before." ]'
                        ]
df.add_system_transition(State.ACK_NEVER_TRIED, State.ASK_HOBBY, ack_never_tried_nlg)

### (USER) RECEIVING SPECIFIC HOBBY USER LIKES WHERE HOBBY HAS INFO FOR EMORA

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