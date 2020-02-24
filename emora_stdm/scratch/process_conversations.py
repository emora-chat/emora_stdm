
import regex


class Conversation:

    convo_cap = r'Conversation Id: (.*)'
    rating_cap = r'Rating: (.*)'
    turn_cap = r'[^ ]+ (.*)'

    def __init__(self):
        self.id = None
        self.rating = None
        self.turns = []

def load_conversations(file):
    print("loading", file)
    print()
    conversations = []
    with open(file) as f:
        conversation = None
        for line in f:
            convo = regex.match(Conversation.convo_cap, line)
            if convo:
                if conversation is not None:
                    conversations.append(conversation)
                conversation = Conversation()
                conversation.id = convo.groups()[0]
            rating = regex.match(Conversation.rating_cap, line)
            if rating:
                r = rating.groups()[0]
                if r != '---':
                    conversation.rating = float(r)
            turns = regex.match(Conversation.turn_cap, line)
            if turns:
                conversation.turns.append(turns.groups()[0])
    return conversations

if __name__ == '__main__':

    conversations = load_conversations('convos_2020-02-21_2020-02-22.txt')

    low_rated = 0
    low_rated_and_movie = 0
    low_rated_movie_noquery = 0

    for convo in conversations:
        if convo.rating and convo.rating <= 2.0:
            low_rated += 1
            is_movie_convo = False
            for i in range(len(convo.turns) - 2):
                a = convo.turns[i]
                b = convo.turns[i+1]
                c = convo.turns[i+2]
                if 'movie plot and reviews' in a \
                        or 'movie-related information' in a \
                        or 'fresh movies' in a:
                    is_movie_convo = True
                if 'what was the last movie you liked?' in a \
                    and ('Here are three' in c
                        or 'Here is a good fresh' in c
                        or 'I have found some' in c):
                    low_rated_movie_noquery += 1
                    print(convo.id)
                    print(a)
                    print(b)
                    print(c)
                    print()
            if is_movie_convo:
                low_rated_and_movie += 1


    print('Low rated conversations:', low_rated)
    print('Low rated convos w/ movie:', low_rated_and_movie)
    print('Low rated convos w/ movie and issue:', low_rated_movie_noquery)