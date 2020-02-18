from emora_stdm import DialogueFlow, Macro
from enum import Enum
from emora_stdm import NatexNLG
import json, os
import random


# states are typically represented as an enum
class State(Enum):
    START = 0
    END = 1
    PETS_Y = 2
    ASK_PETS = 3
    ASK_PETS_N = 4

    FIRST_PET_DOG = 5
    FIRST_PET_CAT = 6
    FIRST_PET_OTHER = 7
    FIRST_PET_DOG_ANS = 8
    FIRST_PET_CAT_ANS = 9
    FIRST_PET_OTHER_ANS = 10
    FIRST_PET_DOG_UNKNOWN = 11
    FIRST_PET_CAT_UNKNOWN = 12
    FIRST_PET_OTHER_UNKNOWN = 13
    FIRST_PET_DOG_BREED_ANS = 14
    FIRST_PET_CAT_BREED_ANS = 15
    FIRST_PET_DOG_BREED = 16
    FIRST_PET_CAT_BREED = 17
    FIRST_PET_OTHER_BREED = 18
    FIRST_PET_DOG_NAME = 19
    FIRST_PET_CAT_NAME = 20
    FIRST_PET_OTHER_NAME = 21
    FIRST_PET_DOG_NAME_ANS = 22
    FIRST_PET_CAT_NAME_ANS = 23
    FIRST_PET_OTHER_NAME_ANS = 24
    FIRST_PET_DOG_FOOD = 25
    FIRST_PET_CAT_FOOD = 26
    FIRST_PET_OTHER_FOOD = 27
    FIRST_PET_DOG_FOOD_ANS = 28
    FIRST_PET_CAT_FOOD_ANS = 29
    FIRST_PET_OTHER_FOOD_ANS = 30

    NO_NO_PETS = 31
    NO_PETS = 32
    NO_PETS_Y = 33
    NO_PETS_N = 34
    NO_PETS_UNKNOWN = 35
    NO_NO_PETS_NO = 36

    FAVORITE_PET_DOG = 37
    FAVORITE_PET = 38
    PETS_UNKNOWN = 39
    FAVORITE_PET_CAT = 40
    FAVORITE_PET_DOG_ANS = 41
    FAVORITE_PET_CAT_ANS = 42
    FAVORITE_PET_DOG_BREED = 43
    FAVORITE_PET_CAT_BREED = 44
    FAVORITE_PET_OTHER = 45
    FAVORITE_PET_OTHER_ANS = 46
    FAVORITE_PET_OTHER_BREED = 47
    FAVORITE_PET_UNKNOWN = 48
    FAVORITE_PET_UNKNOWN_DOG = 49
    FAVORITE_PET_DOG_UNKNOWN = 50
    FAVORITE_PET_CAT_UNKNOWN = 51
    FAVORITE_PET_OTHER_UNKNOWN = 52

    DOG_INTERESTING = 53
    CAT_INTERESTING = 54
    OTHER_INTERESTING = 55
    DOG_INTERESTING_Y = 56
    CAT_INTERESTING_Y = 57
    OTHER_INTERESTING_Y = 58
    DOG_INTERESTING_N = 59
    CAT_INTERESTING_N = 60
    OTHER_INTERESTING_N = 61

    PETS_Y_1 = 62
    PETS_Y_2 = 63

    START_PET = 64
    START_PET_Q = 65

    # ASK_PETS_Y = 64
    # FIRST_PET = 65


class CATCH(Macro):
    def __init__(self, list):
        self.list = list

    def run(self, ngrams, vars, args):
        return ngrams & self.list


class EMORA(Macro):
    def run(self, ngrams, vars, args):
        if args[0] in ("cat", "cats"):
            response = "my favorite cat is toyger."
        elif args[0] in ("dog", "dogs"):
            response = "my favorite dog is german shepherd."
        elif args[0] in ("pet", "pets"):
            response = "my favorite pet is german shepherd dog."
        else:
            response = "my favorite pet is german shepherd dog."
        return response


class INTERESTING(Macro):
    def __init__(self, path):
        self.path = path
        self.count = 0
        with open(self.path, 'r') as f:
            self.db = json.load(f)
        self.db_backup = self.db.copy()

    def run(self, ngrams, vars, args):
        # if self.count < 9:
        #     key = random.randrange(self.count,self.count+5)
        #     self.count += 5
        # else:
        #     self.count = 0
        #     key = random.randrange(self.count,self.count+5)
        #     self.count += 1
        # print(self.count)
        length = len(self.db)
        print(length)
        if length > 2:
            key = random.randrange(length)
            response = self.db.pop(key)
        else:
            self.db = self.db_backup.copy()
            key = random.randrange(length)
            response = self.db.pop(key)
        # return self.db[key]
        return response


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


TRANSITION_OUT = ["movies", "movie", "music", "sports", "sport", "travel"]
NULL = "NULL TRANSITION"
PET_TYPE = {"dog", "dogs", "cat", "cats", "pet", "pets"}
PET_TYPE_OTHER = {"alpaca","alpacas", "camel", "camels", "cattle", "cattles", "skunk", "skunks", "donkey",
            "donkeys", "ferret", "ferrets", "goat", "goats", "hedgehog", "hedgehogs", "horse", "horses", "llama", "llamas", "pig",
            "pigs", "rabbit", "rabbits", "red fox", "red foxes", "rodent", "rodents", "sheep", "sugar gliders", "bird", "birds", "fish",
            "fishes", "arthropod", "arthropods"}
PET_TYPE_TOTAL = {"dog", "dogs", "cat", "cats", "pet", "pets", "alpaca","alpacas", "camel", "camels", "cattle", "cattles", "skunk", "skunks", "donkey",
            "donkeys", "ferret", "ferrets", "goat", "goats", "hedgehog", "hedgehogs", "horse", "horses", "llama", "llamas", "pig",
            "pigs", "rabbit", "rabbits", "red fox", "red foxes", "rodent", "rodents", "sheep", "sugar gliders", "bird", "birds", "fish",
            "fishes", "arthropod", "arthropods"}

macros = {
    'DOG_BREED': BREED(os.path.join('modules','dog_breed_database.json')),
    'DOG_BREED_DESC': BREED_DESC(os.path.join('modules','dog_breed_database.json')),
    'CAT_BREED': BREED(os.path.join('modules','cat_breed_database.json')),
    'CAT_BREED_DESC': BREED_DESC(os.path.join('modules','cat_breed_database.json')),
    'OTHER_BREED': BREED(os.path.join('modules','other_breed_database.json')),
    'OTHER_BREED_DESC': BREED_DESC(os.path.join('modules','other_breed_database.json')),
    'CATCH_PET_TYPE':CATCH(PET_TYPE),
    'CATCH_PET_TYPE_OTHER':CATCH(PET_TYPE_OTHER),
    'CATCH_PET_TYPE_TOTAL':CATCH(PET_TYPE_TOTAL),
    'EMORA':EMORA(),
    'DOG_INTERESTING':INTERESTING(os.path.join('modules','dog_interesting_database.json')),
    'CAT_INTERESTING':INTERESTING(os.path.join('modules','cat_interesting_database.json')),
    'OTHER_INTERESTING':INTERESTING(os.path.join('modules','other_interesting_database.json'))
}

# initialize the DialogueFlow object, which uses a state-machine to manage dialogue
df = DialogueFlow(State.START, initial_speaker=DialogueFlow.Speaker.USER, macros=macros)

# df.add_user_transition(State.START, State.ASK_PETS_Y, '[{pet, pets}]')
# df.add_user_transition(State.START, State.ASK_PETS_Y, '[![!i have] {pet, pets}]')
# df.add_user_transition(State.START, State.FIRST_PET_ANS, '[![!i, have] {dog, dogs, cat, cats}]')
# df.add_user_transition(State.START, State.ASK_PETS_N, '[![!i, dont, have] {dog, dogs}]') # This didn't work well with next line at the same time

# User Turn
df.add_user_transition(State.START, State.PETS_Y, '[$type=#CATCH_PET_TYPE_TOTAL()]')
df.add_user_transition(State.START, State.PETS_Y_1, '[$type=#DOG_BREED()]')
df.add_user_transition(State.START, State.PETS_Y_2, '[$type=#CAT_BREED()]')

df.set_error_successor(State.START, State.START)
df.add_system_transition(State.START, State.START, NULL)
# df.add_system_transition(State.START_PET, State.START_PET_Q, '"I like pets very much, especially dogs. Do you want to talk about pets?"')
# df.add_user_transition(State.START_PET_Q, State.PETS_Y, '[{yes, yea, yup, yep, i do, yeah, a little, sure, of course, i have, i am, sometimes, too, as well, also, agree}]')
# df.add_user_transition(State.START_PET_Q, State.NO_NO_PETS_NO, '[{no, nope, dont}]')

df.add_system_transition(State.START_PET, State.ASK_PETS, '"ok, i was curious about this. Do you have any pets at home? like a dog, cat, or other animals?"')

# System Turn
df.add_system_transition(State.PETS_Y, State.ASK_PETS, '"that\'s great! I love" $type "! actually, " #EMORA($type) "Do you have any pets at your home now? like a dog, cat, or other animals?"')
df.add_system_transition(State.PETS_Y_1, State.ASK_PETS, '"that\'s great! I love" $type "! actually, " #EMORA($type) "Do you have any pets at your home now? like a dog, cat, or other animals?"')
df.add_system_transition(State.PETS_Y_2, State.ASK_PETS, '"that\'s great! I love" $type "! actually, " #EMORA($type) "Do you have any pets at your home now? like a dog, cat, or other animals?"')

# df.add_user_transition(State.ASK_PETS, State.ASK_PETS_Y, '[{yes, yea, yup, yep, i do, yeah, a little, sure, of course, i have, i am, sometimes, too, as well, also, agree, ok, okay}]')

# User Turn
df.add_user_transition(State.ASK_PETS, State.ASK_PETS_N, '[{no, nope, dont}]')
df.add_user_transition(State.ASK_PETS, State.FIRST_PET_DOG, '[{dog, dogs}]')
df.add_user_transition(State.ASK_PETS, State.FIRST_PET_CAT, '[{cat, cats}]')
df.add_user_transition(State.ASK_PETS, State.FIRST_PET_OTHER, '[{other, others}]')
df.add_user_transition(State.ASK_PETS, State.FIRST_PET_OTHER_BREED, '[$breed=#OTHER_BREED()]')
df.add_user_transition(State.ASK_PETS, State.FIRST_PET_DOG_BREED, '[$breed=#DOG_BREED()]')
df.add_user_transition(State.ASK_PETS, State.FIRST_PET_CAT_BREED, '[$breed=#CAT_BREED()]')
df.set_error_successor(State.ASK_PETS, State.FIRST_PET_OTHER_UNKNOWN)

# df.add_system_transition(State.ASK_PETS_UNKNOWN, State.ASK_PETS_UNKNOWN_ANS, '"Sorry, I was sleeping just now. What did you mean? If you mean you have a pet, what is it? If you mean you don\'t have a pet, do you want to know something about the pets?"')
# df.add_user_transition(State.ASK_PETS_UNKNOWN_ANS, State.FIRST_PET_DOG, '[$breed=#DOG_BREED()]')
# df.add_user_transition(State.ASK_PETS_UNKNOWN_ANS, State.FIRST_PET_CAT, '[$breed=#CAT_BREED()]')
# df.add_user_transition(State.ASK_PETS_UNKNOWN_ANS, State.FIRST_PET_OTHER, '[$breed=#OTHER_BREED()]')
# df.set_error_successor(State.ASK_PETS_UNKNOWN_ANS, State.ASK_PETS_UNKNOWN)

# df.add_system_transition(State.ASK_PETS_Y, State.FIRST_PET, '"Cool! What is it? is it a cat, a dog or other types of pets?"')
# df.add_user_transition(State.FIRST_PET, State.FIRST_PET_DOG, '[{dog, dogs}]')
# df.add_user_transition(State.FIRST_PET, State.FIRST_PET_CAT, '[{cat, cats}]')
# df.add_user_transition(State.FIRST_PET, State.FIRST_PET_DOG_BREED_ANS, '[$breed=#DOG_BREED()]')
# df.add_user_transition(State.FIRST_PET, State.FIRST_PET_CAT_BREED_ANS, '[$breed=#CAT_BREED()]')
# df.add_user_transition(State.FIRST_PET, State.FIRST_PET_OTHER, '[$breed=#CATCH_PET_TYPE_OTHER()]')
# df.set_error_successor(State.FIRST_PET, State.FIRST_PET_ANS)
# df.set_error_successor(State.FIRST_PET, State.FIRST_PET_UNKNOWN)
# df.add_system_transition(State.FIRST_PET_UNKNOWN, State.FIRST_PET_NAME, '"Sorry, I\'m not quite familiar with this animal. But I would like to talk about it with you. Can you tell me more information of it? it must have a cute name. What is its name?"')

# System Turn
df.add_system_transition(State.ASK_PETS_N, State.NO_PETS, '"Me neither. Because my dad, doesn\'t let me keep a dog. then, Would you consider getting a pet? i mean, after all, they are so cute."')
# User Turn
df.add_user_transition(State.NO_PETS, State.NO_PETS_Y, '[{yes, yea, yup, yep, i do, yeah, a little, sure, of course, i have, i am, sometimes, too, as well, also, agree}]')
df.add_user_transition(State.NO_PETS, State.NO_PETS_N, '[{no, nope, dont}]')
df.set_error_successor(State.NO_PETS, State.NO_PETS_UNKNOWN)
# System Turn
df.add_system_transition(State.NO_PETS_UNKNOWN, State.FAVORITE_PET_UNKNOWN_DOG, '"I see..., but I like dogs. Do you want to talk about dogs?"')
# User Turn
df.add_user_transition(State.FAVORITE_PET_UNKNOWN_DOG, State.FAVORITE_PET_DOG, '[{yes, yea, yup, yep, i do, yeah, a little, sure, of course, i have, i am, sometimes, too, as well, also, agree, ok, okay}]')
df.add_user_transition(State.FAVORITE_PET_UNKNOWN_DOG, State.NO_NO_PETS_NO, '[{no, nope, dont}]')
df.set_error_successor(State.FAVORITE_PET_UNKNOWN_DOG, State.NO_NO_PETS_NO)

# System Turn
df.add_system_transition(State.NO_PETS_Y, State.FAVORITE_PET, '"Cool, I suggest to adopt instead of buying. i love both dogs and cats. but they can be quite different. which one would you prefer to be your companion?"')
df.add_user_transition(State.FAVORITE_PET, State.FAVORITE_PET_DOG, '[{dog, dogs}]')
df.add_user_transition(State.FAVORITE_PET, State.FAVORITE_PET_CAT, '[{cat, cats}]')
df.add_user_transition(State.FAVORITE_PET, State.FAVORITE_PET_OTHER, '[{other, others}]')
df.add_user_transition(State.FAVORITE_PET, State.FAVORITE_PET_DOG_BREED, '[$breed=#DOG_BREED()]')
df.add_user_transition(State.FAVORITE_PET, State.FAVORITE_PET_CAT_BREED, '[$breed=#CAT_BREED()]')
df.add_user_transition(State.FAVORITE_PET, State.FAVORITE_PET_OTHER_BREED, '[$breed=#OTHER_BREED()]')
df.set_error_successor(State.FAVORITE_PET, State.FAVORITE_PET_UNKNOWN)
df.add_system_transition(State.FAVORITE_PET_UNKNOWN, State.FAVORITE_PET_UNKNOWN_DOG, '"Wow! that\'great! But I\'m not quite familiar with this animal. I like dogs most. Do you want to know more about dogs?"')

df.add_system_transition(State.NO_PETS_N, State.NO_NO_PETS, '"Oh ok, that\'s fine. it is indeed a big decision to introduce new members into your family or life. I like dogs most. Although you won\'t keep a pet, do you want to talk about dogs?"')
df.add_user_transition(State.NO_NO_PETS, State.FAVORITE_PET_DOG, '[{yes, yea, yup, yep, i do, yeah, a little, sure, of course, i have, i am, sometimes, too, as well, also, agree, ok, okay}]')
df.add_user_transition(State.NO_NO_PETS, State.NO_NO_PETS_NO, '[{no, nope, dont}]')
df.set_error_successor(State.NO_NO_PETS, State.NO_NO_PETS_NO)
df.add_system_transition(State.NO_NO_PETS_NO, State.END, '" "')
# df.set_error_successor(State.NO_NO_PETS, State.START_OTHER)
# df.add_user_transition(State.NO_NO_PETS, State.START_OTHER, TRANSITION_OUT)
# df.set_error_successor(State.NO_NO_PETS_YES, State.START_OTHER)
# df.set_error_successor(State.NO_NO_PETS_NO, State.START_OTHER)
# df.add_system_transition(State.NO_NO_PETS_YES, State.FAVORITE_PET, '"I like dogs best! Which do you want to talk about? Dogs or cats?"')

df.add_system_transition(State.FIRST_PET_DOG, State.FIRST_PET_DOG_ANS, '"Wow! that\'s great! I like dogs! What is its breed? I mean it\'s german shepherd, golden retrieval, husky, or other dog breed?"')
df.add_system_transition(State.FIRST_PET_CAT, State.FIRST_PET_CAT_ANS, '"Wow! that\'s great! I like cats! What is its breed? I mean it\'s turkish angora, toyger, or other cat breed?"')
df.add_system_transition(State.FIRST_PET_OTHER, State.FIRST_PET_OTHER_ANS, '"Wow! that\'s interesting! What is it? A fish? a bird?"')

df.add_user_transition(State.FIRST_PET_DOG_ANS, State.FIRST_PET_DOG_BREED, '[$breed=#DOG_BREED()]')
df.add_user_transition(State.FIRST_PET_CAT_ANS, State.FIRST_PET_CAT_BREED, '[$breed=#CAT_BREED()]')
df.add_user_transition(State.FIRST_PET_OTHER_ANS, State.FIRST_PET_OTHER_BREED, '[$breed=#OTHER_BREED()]')
df.set_error_successor(State.FIRST_PET_DOG_ANS, State.FIRST_PET_DOG_UNKNOWN)
df.set_error_successor(State.FIRST_PET_CAT_ANS, State.FIRST_PET_CAT_UNKNOWN)
df.set_error_successor(State.FIRST_PET_OTHER_ANS, State.FIRST_PET_OTHER_UNKNOWN)

# System Turn - Ask Name
df.add_system_transition(State.FIRST_PET_DOG_BREED, State.FIRST_PET_DOG_NAME, '"Wow! Sounds interesting!" #DOG_BREED_DESC($breed) "I guess it must have a cute name. How did you choose the name?"')
df.add_system_transition(State.FIRST_PET_CAT_BREED, State.FIRST_PET_CAT_NAME, '"Wow! Sounds interesting!" #CAT_BREED_DESC($breed) "I guess it must have a cute name. How did you choose the name?"')
df.add_system_transition(State.FIRST_PET_OTHER_BREED, State.FIRST_PET_OTHER_NAME, '"Wow! Sounds interesting. " #OTHER_BREED_DESC($breed)"I guess it must have a cute name. How did you choose the name?"')
df.add_system_transition(State.FIRST_PET_DOG_UNKNOWN, State.FIRST_PET_DOG_NAME, '"Wow! Sounds interesting. Although I am not quite familiar with this dog breed, I guess it must have a cute name. How did you choose the name?"')
df.add_system_transition(State.FIRST_PET_CAT_UNKNOWN, State.FIRST_PET_CAT_NAME, '"Wow! Sounds interesting. Although I am not quite familiar with this cat breed, I guess it must have a cute name. How did you choose the name?"')
df.add_system_transition(State.FIRST_PET_OTHER_UNKNOWN, State.FIRST_PET_OTHER_NAME, '"Wow! Sounds interesting. Although I am not quite familiar with this kind of pets, I guess it must have a cute name. How did you choose the name?"')
# User Turn - Answer Name
df.set_error_successor(State.FIRST_PET_DOG_NAME, State.FIRST_PET_DOG_NAME_ANS)
df.set_error_successor(State.FIRST_PET_CAT_NAME, State.FIRST_PET_CAT_NAME_ANS)
df.set_error_successor(State.FIRST_PET_OTHER_NAME, State.FIRST_PET_OTHER_NAME_ANS)

# System Turn - Ask Food
df.add_system_transition(State.FIRST_PET_DOG_NAME_ANS, State.FIRST_PET_DOG_FOOD, '"Oh! That\'s so sweet! If I had a dog, I would just named it puppy in a lazy way. So, what do you usually feed it? do you prepare the pet food by yourself or purchase pet food from the food market?"')
df.add_system_transition(State.FIRST_PET_CAT_NAME_ANS, State.FIRST_PET_CAT_FOOD, '"Oh! That\'s so sweet! If I had a cat, I would just named it kitty in a lazy way. So, what do you usually feed it? do you prepare the pet food by yourself or purchase pet food from the food market?"')
df.add_system_transition(State.FIRST_PET_OTHER_NAME_ANS, State.FIRST_PET_OTHER_FOOD, '"Oh! That\'s so sweet! If I had a dog, I would just named it puppy in a lazy way. So, what do you usually feed it? do you prepare the pet food by yourself or purchase pet food from the food market?"')
# User Turn - Answer Food
df.set_error_successor(State.FIRST_PET_DOG_FOOD, State.FIRST_PET_DOG_FOOD_ANS)
df.set_error_successor(State.FIRST_PET_CAT_FOOD, State.FIRST_PET_CAT_FOOD_ANS)
df.set_error_successor(State.FIRST_PET_OTHER_FOOD, State.FIRST_PET_OTHER_FOOD_ANS)

# System Turn
df.add_system_transition(State.FIRST_PET_DOG_FOOD_ANS, State.DOG_INTERESTING, '"that\'s nice! you know, there are lots of food that dogs can\'t eat, like"{cooked bones, onions, garlic, chocolate, coffee or caffeine products, sultanas, currants, nuts}".I know lots of interesting things about dogs, would you like to listen one? "')
df.add_system_transition(State.FIRST_PET_CAT_FOOD_ANS, State.CAT_INTERESTING, '"that\'s nice! you know, there are lots of food that cats can\'t eat, like"{alcohol, chocolate, coffee, tea, energy drinks, cheese, milk, raw meat, raw eggs, raw fish, grapes, raisins, onions, garlic, xylitolts}".I know lots of interesting things about cats, would you like to listen one? "')
df.add_system_transition(State.FIRST_PET_OTHER_FOOD_ANS, State.OTHER_INTERESTING, '"that\'s nice! I love being companied by pets because they are so intelligent and warm hearted beings. I know lots of interesting things about pets, would you like to listen one?"')
# User Turn
df.add_user_transition(State.DOG_INTERESTING, State.DOG_INTERESTING_Y, '[{yes, yea, yup, yep, i do, yeah, a little, sure, of course, i have, i am, sometimes, too, as well, also, agree, ok, okay}]')
df.add_user_transition(State.DOG_INTERESTING, State.DOG_INTERESTING_N, '[{no, nope, dont}]')
df.add_user_transition(State.CAT_INTERESTING, State.CAT_INTERESTING_Y, '[{yes, yea, yup, yep, i do, yeah, a little, sure, of course, i have, i am, sometimes, too, as well, also, agree, ok, okay}]')
df.add_user_transition(State.CAT_INTERESTING, State.CAT_INTERESTING_N, '[{no, nope, dont}]')
df.add_user_transition(State.OTHER_INTERESTING, State.OTHER_INTERESTING_Y, '[{yes, yea, yup, yep, i do, yeah, a little, sure, of course, i have, i am, sometimes, too, as well, also, agree, ok, okay}]')
df.add_user_transition(State.OTHER_INTERESTING, State.OTHER_INTERESTING_N, '[{no, nope, dont}]')

# Error
df.set_error_successor(State.DOG_INTERESTING, State.DOG_INTERESTING_N)
df.set_error_successor(State.CAT_INTERESTING, State.CAT_INTERESTING_N)
df.set_error_successor(State.OTHER_INTERESTING, State.OTHER_INTERESTING_N)

# System Turn
df.add_system_transition(State.DOG_INTERESTING_Y, State.DOG_INTERESTING, '#DOG_INTERESTING()".Do you want to know more?"')
df.set_error_successor(State.DOG_INTERESTING_Y, State.DOG_INTERESTING_N)
df.add_system_transition(State.DOG_INTERESTING_N, State.END, '" "')
df.add_system_transition(State.CAT_INTERESTING_Y, State.CAT_INTERESTING, '#CAT_INTERESTING()".Do you want to know more?"')
df.set_error_successor(State.CAT_INTERESTING_Y, State.CAT_INTERESTING_N)
df.add_system_transition(State.CAT_INTERESTING_N, State.END, '" "')
df.add_system_transition(State.OTHER_INTERESTING_Y, State.OTHER_INTERESTING, '#OTHER_INTERESTING()".Do you want to know more?"')
df.set_error_successor(State.OTHER_INTERESTING_Y, State.OTHER_INTERESTING_N)
df.add_system_transition(State.OTHER_INTERESTING_N, State.END, '" "')

df.add_system_transition(State.FAVORITE_PET_DOG, State.FAVORITE_PET_DOG_ANS, '"Nice choice! I like dogs, too! Among various dog breeds, which one do you like the best? I mean, like german shepherd, golden retrieval, husky, or other dog breed?"')
df.add_user_transition(State.FAVORITE_PET_DOG_ANS, State.FAVORITE_PET_DOG_BREED, '[$breed=#DOG_BREED()]')
df.set_error_successor(State.FAVORITE_PET_DOG_ANS, State.FAVORITE_PET_DOG_UNKNOWN)
df.add_system_transition(State.FAVORITE_PET_DOG_UNKNOWN, State.DOG_INTERESTING, '"Cool! although i know lots of dog breed, I\'m not quite familiar with the one you mentioned, but i\'m sure they must very lovable in some way. Also, I know lots of interesting things about dogs. would you like to listen one?"')
df.add_system_transition(State.FAVORITE_PET_DOG_BREED, State.DOG_INTERESTING, '"Awesome! they are great!" #DOG_BREED_DESC($breed) "I may adopt one in the future! I know lots of interesting things about dogs. would you like to listen one?"')


df.add_system_transition(State.FAVORITE_PET_CAT, State.FAVORITE_PET_CAT_ANS, '"Good choice! Among various cat breeds, what specific kind is your favorite? I mean, like turkish angora, toyger, or other cat breed?"')
df.add_user_transition(State.FAVORITE_PET_CAT_ANS, State.FAVORITE_PET_CAT_BREED, '[$breed=#CAT_BREED()]')
df.set_error_successor(State.FAVORITE_PET_CAT_ANS, State.FAVORITE_PET_CAT_UNKNOWN)
df.add_system_transition(State.FAVORITE_PET_CAT_UNKNOWN, State.CAT_INTERESTING, '"Cool! although i know lots of cat breed, I\'m not quite familiar with the one you mentioned, but i\'m sure they must very lovable in some way. Also, I know lots of interesting things about cats. would you like to listen one?"')
df.add_system_transition(State.FAVORITE_PET_CAT_BREED, State.CAT_INTERESTING, '"Awesome! they are wonderful creatures!" #CAT_BREED_DESC($breed) "I may consider adopt one in the future! I know lots of interesting things about cats. would you like to listen one?"')

df.add_system_transition(State.FAVORITE_PET_OTHER, State.FAVORITE_PET_OTHER_ANS, '"there are lots of other types of pets, i am curious what it is, a bird? or a rabbit? or other pets?"')
df.add_user_transition(State.FAVORITE_PET_OTHER_ANS, State.FAVORITE_PET_OTHER_BREED, '[$breed=#CAT_BREED()]')
df.set_error_successor(State.FAVORITE_PET_OTHER_ANS, State.FAVORITE_PET_OTHER_UNKNOWN)
df.add_system_transition(State.FAVORITE_PET_OTHER_UNKNOWN, State.OTHER_INTERESTING, '"oops, sorry, although i know people love all kinds of animals, I\'m not quite familiar with the one you mentioned, but i\'m sure they must very lovable in some way. Also, I know lots of interesting things about pets. would you like to listen one?"')
df.add_system_transition(State.FAVORITE_PET_OTHER_BREED, State.OTHER_INTERESTING, '"Awesome! they are wonderful creatures!" #OTHER_BREED_DESC($breed) "I may consider keep one in the future! I know lots of interesting things about pets. would you like to listen one?"')

df.update_state_settings(State.END, system_multi_hop=True)
df.add_system_transition(State.END, State.END, '" "')
# end (recurrent) the dialogue

if __name__ == '__main__':
    # automatic verification of the DialogueFlow's structure (dumps warnings to stdout)
    df.check()
    # run the DialogueFlow in interactive mode to test
    df.run(debugging=True)