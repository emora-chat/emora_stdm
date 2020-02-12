#from nltk.corpus import wordnet as wn
import random
import time

required_context = ['text']

#from amazon's nounner
np_ignore_list = ["'s", 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
                  "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
                  'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs',
                  'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
                  'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
                  'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about',
                  'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up',
                  'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there',
                  'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
                  'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can',
                  'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain',
                  'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn',
                  "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn',
                  "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't",
                  'wouldn', "wouldn't", "my name", "your name", "wow", "yeah", "yes", "ya", "cool", "okay", "more", "some more",
                  " a lot", "a bit", "another one", "something else", "something", "anything", "someone", "anyone", "play", "mean",
                  "a lot", "a little", "a little bit", "lets", "let's"]

filler = ['huh', 'hmm', 'ok', 'so', 'well', 'oh']
its = ['its', 'it is']
interest_syns = ['interesting', 'cool']
mention_syns = ['mentioned', 'said', 'thought of', 'talked about']
dont = ['do not', 'dont']
think_syns = ['think', 'believe', 'know if', 'remember if', 'recall if']
ive = ['ive', 'i have']
recently_syns = ['recently', 'in a while', 'in the last few days']
see_syns = ['see', 'think', 'believe']
on_your_mind_syns = ['on your mind', 'in your thoughts']
qual_syns = ['interesting', 'compelling']
noun = ['*NOUN*']

beginning = ['thats interesting.', 'i didnt know that.', 'thanks for sharing that with me.']
qualification = ["you know", "i just want to mention that"]
redirect = ["I really enjoy talking about movies.", "I am up to date with the latest movies."]
direct = ["just let me know if you want to talk about movies", "feel free to tell me if you are interested in movies"]
prompt = ["which one interests you most?", "im wondering which one of these interests you?"]

def get_required_context():
    return required_context

def handle_message(msg):
    max = 1

    if msg['fallbackcount'][1] is not None:
        fallbackcount = int(msg['fallbackcount'][1])
    else:
        fallbackcount = 0

    if msg['chosenModule'][1] == 'fallbacktransitions':
        fallbackcount += 1

    # if fallbackcount == max: # redirect to handled topic
    #     if msg['chosenModule'][1] == 'fallbacktransitions':
    #         response = random.choice(beginning) + ' ' + random.choice(qualification) + ' ' \
    #                    + random.choice(redirect) + ' ' + random.choice(direct)
    #         fallbackcount += 1
    #         return {"response": response, "score": 0.60,
    #                 "context_manager":
    #                     {
    #                         "fallbackcount": fallbackcount,
    #                         "spoken_ackn": -1,
    #                         "spoken_qn": -1,
    #                         "selected_ackn": -1,
    #                         "selected_qn": -1
    #                     }
    #                 }
    #     else:
    #         fallbackcount = 0

    if fallbackcount >= max: # do not respond
        if msg['chosenModule'][1] == 'fallbacktransitions':
            fallbackcount += 1
            response = ''
            return {"response": response, "score": 0.0,
                    "context_manager":
                        {
                            "fallbackcount": fallbackcount,
                            "spoken_ackn": -1,
                            "spoken_qn": -1,
                            "selected_ackn": -1,
                            "selected_qn": -1
                        }
                    }
        else:
            return {"response": '', "score": 0.0,
                    "context_manager":
                        {
                            "fallbackcount": fallbackcount,
                            "spoken_ackn": -1,
                            "spoken_qn": -1,
                            "selected_ackn": -1,
                            "selected_qn": -1
                        }
                    }

    spoken_ackn = -1
    spoken_qn = -1
    if msg['selected_ackn'][1] is not None and msg['chosenModule'][1] is not None:
        if msg['chosenModule'][1] == "fallbacktransitions":
            spoken_ackn = int(msg['selected_ackn'][1]) # selected_ackn stores index selected on last turn
        else:
            spoken_ackn = int(msg['spoken_ackn'][1]) # spoken_ackn stores index of ack that was last spoken (even if more than one turn ago)

    if msg['selected_qn'][1] is not None and msg['chosenModule'][1] is not None:
        if msg['chosenModule'][1] == "fallbacktransitions":
            spoken_qn = int(msg['selected_qn'][1]) # selected_qn stores index selected on last turn
        else:
            spoken_qn = int(msg['spoken_qn'][1]) # spoken_qn stores index of qn that was last spoken (even if more than one turn ago)

    input_text = msg['text'][0].lower()
    noun_phrases = []
    if msg['nounner'][0] is not None and 'user_input_noun_phrases' in msg['nounner'][0]:
        noun_phrases = msg['nounner'][0]['user_input_noun_phrases']

    i = 3
    ack_opts = list(range(0, i))
    if spoken_ackn in ack_opts:
        ack_opts.remove(spoken_ackn)
    ackn = random.choice(ack_opts)
    if ackn == 0:
        ack = '{}, i think {} {} that you {} *NOUN*.'.format(random.choice(filler),
                                                              random.choice(its),
                                                              random.choice(interest_syns),
                                                              random.choice(mention_syns))
    elif ackn == 1:
        ack = 'i {} {} {} thought of {} {}.'.format(random.choice(dont),
                                                       random.choice(think_syns),
                                                       random.choice(ive),
                                                       random.choice(noun),
                                                       random.choice(recently_syns))
    elif ackn == 2:
        ack = 'i {} you are interested in *NOUN*.'.format(random.choice(see_syns))

    j = 3
    q_opts = list(range(0, j))
    if spoken_qn in q_opts:
        q_opts.remove(spoken_qn)
    qn = random.choice(q_opts)
    if qn == 0:
        q = 'why is that {}?'.format(random.choice(on_your_mind_syns))
    elif qn == 1:
        q = "what do you think about it?"
    elif qn == 2:
        q = "can you tell me more about your opinion on it?"
    elif qn == 3:
        q = "what do you find the most {} about it?".format(random.choice(qual_syns))

    response = ack + ' ' + q
    input_text_split = input_text.split()
    new_input_text = []
    for token in input_text_split:
        if token in ['i', 'me']:
            new_input_text.append("you")
        elif token in ['my']:
            new_input_text.append("your")
        elif token in ['you']:
            new_input_text.append("i")
        elif token in ['your']:
            new_input_text.append("my")
        else:
            new_input_text.append(token)
    input_text = ' '.join(new_input_text)
    if "*NOUN*" in response:
        if len(noun_phrases) > 0:
            choices = []
            for np in noun_phrases:
                if np not in np_ignore_list:
                    choices.append(np)
            if len(choices) > 0:
                chosen = random.choice(choices)
                new_chosen = []
                for token in chosen.split():
                    if token in ['i', 'me']:
                        new_chosen.append("you")
                    elif token in ['my']:
                        new_chosen.append("your")
                    elif token in ['you']:
                        new_chosen.append("i")
                    elif token in ['your']:
                        new_chosen.append("my")
                    else:
                        new_chosen.append(token)
                chosen = ' '.join(new_chosen)
                response = response.replace("*NOUN*", chosen)
            else:
                response = ''
        else:
            response = ''

    # some hypernym code
    # k = 2
    # hypernyms = set()
    # for index, wn_object in enumerate(wn.synsets(input_word)):
    #     if index < k:
    #         for types in wn_object.hypernyms():
    #             hypernyms.update(types.lemma_names())
    # print(hypernyms)

    score = 0.0
    if len(response) > 0:
        score = 0.6

    return {"response": response, "score": score,
            "context_manager":
                  {
                     "fallbackcount": fallbackcount,
                      "spoken_ackn": spoken_ackn,
                      "spoken_qn": spoken_qn,
                      "selected_ackn": ackn,
                      "selected_qn": qn
                  }
            }

if __name__ == '__main__':
    start = time.time()
    response = handle_message({'text':"i like my life"})
    print(response, time.time() - start)

    start = time.time()
    response = handle_message({'text': "cars are cool"})
    print(response, time.time() - start)

    start = time.time()
    response = handle_message({'text': "what is happening in russia"})
    print(response, time.time() - start)

    start = time.time()
    response = handle_message({'text': "politics"})
    print(response, time.time() - start)
