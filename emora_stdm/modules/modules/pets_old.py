from emora_stdm import DialogueFlow, Macro, EnumByName
from enum import Enum, auto
from emora_stdm import NatexNLG
import json, os

# states are typically represented as an enum
class State(EnumByName):
    START = auto()
    END = auto()
    PETS_ANS = auto()
    PETS_Y = auto()
    PETS_N = auto()
    PETS_ERR = auto()
    ASK_PETS = auto()
    ASK_PETS_Y = auto()
    ASK_PETS_N = auto()
    FIRST_PET = auto()
    FIRST_PET_ANS = auto()
    NO_PETS = auto()
    NO_PETS_Y = auto()
    NO_PETS_N = auto()
    FAVORITE_PET = auto()
    FAVORITE_PET_DOG = auto()
    FAVORITE_PET_CAT = auto()
    NO_NO_PETS = auto()
    FIRST_PET_SPECIES = auto()
    FIRST_PET_SPECIES_ANS = auto()
    FIRST_PET_NAME = auto()
    FIRST_PET_NAME_ANS = auto()
    FIRST_PET_AGE = auto()
    FIRST_PET_AGE_ANS = auto()
    FIRST_PET_APPEARANCE = auto()
    FIRST_PET_APPEARANCE_ANS = auto()
    FIRST_PET_FOOD = auto()
    FIRST_PET_FOOD_ANS = auto()
    PET_PROS_CONS = auto()
    PET_PROS_CONS_ANS = auto()
    DOG_SPECIES = auto()
    CAT_SPECIES = auto()
    DOG_SPECIES_CERTAIN = auto()
    DOG_SPECIES_CERTAIN_ANS = auto()
    CAT_SPECIES_CERTAIN = auto()
    CAT_SPECIES_CERTAIN_ANS = auto()
    PETS_UNKNOWN = auto()
    START_OTHER = auto()
    ASK_PETS_UNKNOWN = auto()
    FIRST_PET_DOG = auto()
    FIRST_PET_CAT = auto()
    FIRST_PET_OTHER = auto()
    FIRST_PET_UNKNOWN = auto()
    FAVORITE_PET_UNKNOWN = auto()
    FAVORITE_PET_UNKNOWN_DOG = auto()
    NO_NO_PETS_YES = auto()
    NO_PETS_UNKNOWN = auto()
    FAVORITE_PET_OTHER = auto()
    NO_NO_PETS_NO = auto()
    OTHER_SPECIES_CERTAIN = auto()
    OTHER_SPECIES_CERTAIN_ANS = auto()
    OTHER_SPECIES = auto()

class BREED_DESC(Macro):
    def __init__(self, path):
        self.path = path
        with open(self.path, 'r') as f:
            self.db = json.load(f)

    def run(self, ngrams, vars, args):

        return self.db[args[0]]

class BREED(Macro):
    def __init__(self, path):
        self.path = path
        with open(self.path, 'r') as f:
            self.db = json.load(f)

    def run(self, ngrams, vars, args):
        return ngrams & self.db.keys()

macros = {
    'DOG_BREED': BREED(os.path.join('modules','dog_breed_database.json')),
    'DOG_BREED_DESC': BREED_DESC(os.path.join('modules','dog_breed_database.json')),
    'CAT_BREED': BREED(os.path.join('modules','cat_breed_database.json')),
    'CAT_BREED_DESC': BREED_DESC(os.path.join('modules','cat_breed_database.json')),
    'OTHER_BREED': BREED(os.path.join('modules','other_breed_database.json')),
    'OTHER_BREED_DESC': BREED_DESC(os.path.join('modules','other_breed_database.json'))
}

TRANSITION_OUT = ["movies", "music", "sports"]
NULL = "NULL TRANSITION"
PET_TYPE = ["dog", "dogs", "cat", "cats"]
PET_TYPE_OTHER = ["alpaca","alpacas", "camel", "camels", "cattle", "cattles", "skunk", "skunks", "donkey",
            "donkeys", "ferret", "ferrets", "goat", "goats", "hedgehog", "hedgehogs", "horse", "horses", "llama", "llamas", "pig",
            "pigs", "rabbit", "rabbits", "red fox", "red foxes", "rodent", "rodents", "sheep", "sugar gliders", "bird", "birds", "fish",
            "fishes", "arthropod", "arthropods"]

# initialize the DialogueFlow object, which uses a state-machine to manage dialogue
df = DialogueFlow(State.START, initial_speaker=DialogueFlow.Speaker.USER, macros=macros)

df.add_user_transition(State.START, State.PETS_Y, '[{pet,pets}]')
df.set_error_successor(State.START, State.START)
df.add_system_transition(State.START, State.START, NULL)

df.add_system_transition(State.PETS_Y, State.ASK_PETS, '"I love pets! actually, my favorite dog is german shepherd. Do you have any pets?"')
df.update_state_settings(State.PETS_Y, system_multi_hop = True)
df.add_user_transition(State.ASK_PETS, State.ASK_PETS_Y, '[{yes, yea, yup, yep, i do, yeah, a little, sure, of course, i have, i am, sometimes, too, as well, also, agree}]')
df.add_user_transition(State.ASK_PETS, State.ASK_PETS_N, '[{no, nope, dont}]')
df.set_error_successor(State.ASK_PETS, State.ASK_PETS_UNKNOWN)
df.add_system_transition(State.ASK_PETS_UNKNOWN, State.ASK_PETS, '"Sorry, I don \' t understand. Do you have any pets?"')

# df.add_system_transition(State.PETS_N, State.START, '"ok, then, what other topic do you want to talk about, movie or sports?"')
# df.add_user_transition(State.END, State.PETS_Y, '[{pet,pets}]')
# df.add_user_transition(State.END, State.START_OTHER, TRANSITION_OUT)
#
# df.add_system_transition(State.PETS_ERR, State.END, '"i\'m not sure i understand."')

df.add_system_transition(State.ASK_PETS_Y, State.FIRST_PET, '"Cool! What is it? is it a cat, a dog or other types of pets?"')
# df.add_user_transition(State.FIRST_PET, State.FIRST_PET_DOG, '[$breed=#DOG_BREED()]')
# df.add_user_transition(State.FIRST_PET, State.FIRST_PET_CAT, '[$breed=#CAT_BREED()]')
# df.add_user_transition(State.FIRST_PET, State.FIRST_PET_OTHER, '[$breed=#OTHER_BREED()]')
df.set_error_successor(State.FIRST_PET, State.FIRST_PET_ANS)
# df.set_error_successor(State.FIRST_PET, State.FIRST_PET_UNKNOWN)
# df.add_system_transition(State.FIRST_PET_UNKNOWN, State.FIRST_PET_NAME, '"Sorry, I \'m not quite familiar with this animal. But I would like to talk about it with you. Can you tell me more information of it? it must have a cute name. What is its name?"')

df.add_system_transition(State.ASK_PETS_N, State.NO_PETS, '"then, Would you consider getting a pet? i mean, after all, they are so cute."')
df.add_user_transition(State.NO_PETS, State.NO_PETS_Y, '[{yes, yea, yup, yep, i do, yeah, a little, sure, of course, i have, i am, sometimes, too, as well, also, agree}]')
df.add_user_transition(State.NO_PETS, State.NO_PETS_N, '[{no, nope, dont}]')
df.set_error_successor(State.NO_PETS, State.NO_PETS_UNKNOWN)
df.add_system_transition(State.NO_PETS_UNKNOWN, State.FAVORITE_PET_UNKNOWN_DOG, '"I see..., but I like dogs. Do you want to talk about dogs?"')
df.add_user_transition(State.FAVORITE_PET_UNKNOWN_DOG, State.FAVORITE_PET_DOG, '[{yes, yea, yup, yep, i do, yeah, a little, sure, of course, i have, i am, sometimes, too, as well, also, agree}]')
df.add_user_transition(State.FAVORITE_PET_UNKNOWN_DOG, State.NO_NO_PETS_NO, '[{no, nope, dont}]')
df.set_error_successor(State.FAVORITE_PET_UNKNOWN_DOG, State.NO_NO_PETS_NO)

df.add_system_transition(State.NO_PETS_Y, State.FAVORITE_PET, '"Cool, I suggest to adopt instead of buying. i love both dogs and cats. but they can be quite different. which one would you prefer to be your companion?"')
df.add_user_transition(State.FAVORITE_PET, State.FAVORITE_PET_DOG, '[$breed=#DOG_BREED()]')
df.add_user_transition(State.FAVORITE_PET, State.FAVORITE_PET_CAT, '[$breed=#CAT_BREED()]')
df.add_user_transition(State.FAVORITE_PET, State.FAVORITE_PET_OTHER, '[$breed=#OTHER_BREED()]')
df.set_error_successor(State.FAVORITE_PET, State.FAVORITE_PET_UNKNOWN)
df.add_system_transition(State.FAVORITE_PET_UNKNOWN, State.FAVORITE_PET_UNKNOWN_DOG, '"Wow! that \' great! But I \'m not quite familiar with this animal. I like dogs most. Do you want to know more about dogs?"')

df.add_system_transition(State.NO_PETS_N, State.NO_NO_PETS, '"Oh ok, that \'s fine. it is indeed a big decision to introduce new members into your family or life. I like dogs most. Although you won \'t keep a pet, do you want to talk about dogs?"')
df.add_user_transition(State.NO_NO_PETS, State.FAVORITE_PET_DOG, '[{yes, yea, yup, yep, i do, yeah, a little, sure, of course, i have, i am, sometimes, too, as well, also, agree}]')
df.add_user_transition(State.NO_NO_PETS, State.NO_NO_PETS_NO, '[{no, nope, dont}]')
df.set_error_successor(State.NO_NO_PETS, State.NO_NO_PETS_NO)
df.add_system_transition(State.NO_NO_PETS_NO, State.END, '"I see."')
# df.set_error_successor(State.NO_NO_PETS, State.START_OTHER)
# df.add_user_transition(State.NO_NO_PETS, State.START_OTHER, TRANSITION_OUT)
# df.set_error_successor(State.NO_NO_PETS_YES, State.START_OTHER)
# df.set_error_successor(State.NO_NO_PETS_NO, State.START_OTHER)
# df.add_system_transition(State.NO_NO_PETS_YES, State.FAVORITE_PET, '"I like dogs best! Which do you want to talk about? Dogs or cats?"')

# df.add_system_transition(State.FIRST_PET_DOG, State.FIRST_PET_BREED, '"Wow! that \'s great! What is its breed?"')
# df.add_system_transition(State.FIRST_PET_CAT, State.FIRST_PET_BREED, '"Wow! that \'s great! What is its breed?"')
# df.add_system_transition(State.FIRST_PET_OTHER, State.FIRST_PET_OTHER_BREED, '"Wow! that \'s great! What is its breed?"')
df.add_system_transition(State.FIRST_PET_ANS, State.FIRST_PET_SPECIES, '"Wow! that \'s great! What is its breed?"')
df.set_error_successor(State.FIRST_PET_SPECIES, State.FIRST_PET_SPECIES_ANS)

# df.add_user_transition(State.FIRST_PET_DOG_BREED_ANS, State.FIRST_PET_DOG_BREED_ANS_CERTAIN, '[$breed=#DOG_BREED()]')
# df.add_user_transition(State.FIRST_PET_CAT_BREED_ANS, State.FIRST_PET_CAT_BREED_ANS_CERTAIN, '[$breed=#CAT_BREED()]')
# df.add_user_transition(State.FIRST_PET_OTHER_BREED_ANS, State.FIRST_PET_OTHER_BREED_ANS_CERTAIN, '[$breed=#OTHER_BREED()]')
# df.set_error_successor(State.FIRST_PET_SPECIES, State.FIRST_PET_SPECIES_ANS)

df.add_system_transition(State.FIRST_PET_SPECIES_ANS, State.FIRST_PET_NAME, '"it must have a cute name. How did you choose the name?"')
df.set_error_successor(State.FIRST_PET_NAME, State.FIRST_PET_NAME_ANS)

df.add_system_transition(State.FIRST_PET_NAME_ANS, State.FIRST_PET_AGE, '"Oh! That \' s a sweet name! How old is it?"')
df.set_error_successor(State.FIRST_PET_AGE, State.FIRST_PET_AGE_ANS)

df.add_system_transition(State.FIRST_PET_AGE_ANS, State.FIRST_PET_APPEARANCE, '"What does it look like? Is it handsome? is it furry?"')
df.set_error_successor(State.FIRST_PET_APPEARANCE, State.FIRST_PET_APPEARANCE_ANS)

df.add_system_transition(State.FIRST_PET_APPEARANCE_ANS, State.FIRST_PET_FOOD, '"wow! do you prepare the pet food yourself or purchase pet food from the food market?"')
df.set_error_successor(State.FIRST_PET_FOOD, State.FIRST_PET_FOOD_ANS)

df.add_system_transition(State.FIRST_PET_FOOD_ANS, State.PET_PROS_CONS, '"that \' s nice! I love being companied by pets because they are so intelligent and warm hearted beings. what do you think?"')
df.set_error_successor(State.PET_PROS_CONS, State.END)
df.update_state_settings(State.END, system_multi_hop=True)

df.add_system_transition(State.FAVORITE_PET_DOG, State.DOG_SPECIES, '"among various dog breeds, which one do you like the best?"')
df.add_user_transition(State.DOG_SPECIES, State.DOG_SPECIES_CERTAIN, '[$breed=#DOG_BREED()]')
df.set_error_successor(State.DOG_SPECIES, State.PETS_UNKNOWN)
df.add_system_transition(State.PETS_UNKNOWN, State.END, '"oops, sorry, although i know people love all kinds of animals, I \'m not quite familiar with the one you mentioned, but i \' m sure they must very lovable in some way."')
df.add_system_transition(State.DOG_SPECIES_CERTAIN, State.DOG_SPECIES_CERTAIN_ANS, '"Awesome! they are great!" #DOG_BREED_DESC($breed) "I may adopt one in the future!"')
df.set_error_successor(State.DOG_SPECIES_CERTAIN_ANS, State.END)

df.add_system_transition(State.FAVORITE_PET_CAT, State.CAT_SPECIES, '"among various cat breeds, what specific kind is your favorite?"')
df.add_user_transition(State.CAT_SPECIES, State.CAT_SPECIES_CERTAIN, '[$breed=#CAT_BREED()]')
df.set_error_successor(State.CAT_SPECIES, State.PETS_UNKNOWN)
df.add_system_transition(State.CAT_SPECIES_CERTAIN, State.CAT_SPECIES_CERTAIN_ANS, '"Awesome! they are wonderful creatures!" #CAT_BREED_DESC($breed) "I may consider adopt one in the future!"')
df.set_error_successor(State.CAT_SPECIES_CERTAIN_ANS, State.END)

df.add_system_transition(State.FAVORITE_PET_OTHER, State.OTHER_SPECIES, '"among various breeds, what specific kind is your favorite?"')
df.add_user_transition(State.OTHER_SPECIES, State.OTHER_SPECIES_CERTAIN, '[$breed=#OTHER_BREED()]')
df.set_error_successor(State.OTHER_SPECIES, State.PETS_UNKNOWN)
df.add_system_transition(State.OTHER_SPECIES_CERTAIN, State.OTHER_SPECIES_CERTAIN_ANS, '"Awesome! they are wonderful creatures!" #OTHER_BREED_DESC($breed) "I may consider adopt one in the future!"')
df.set_error_successor(State.OTHER_SPECIES_CERTAIN_ANS, State.END)
# end (recurrent) the dialogue

if __name__ == '__main__':
    # automatic verification of the DialogueFlow's structure (dumps warnings to stdout)
    df.check()
    # run the DialogueFlow in interactive mode to test
    df.run(debugging=True)