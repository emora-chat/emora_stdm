from dialogue_flow import DialogueFlow, HIGHSCORE, LOWSCORE

component = DialogueFlow('prestart')

positive_indicators = ['feelings_positive','uppers']
negative_indicators = ['feelings_negative','downers']
feelings_positive = ['happy', 'excited', 'joyful', 'joy', 'thrilled', 'ready', 'good',
                     'great', 'fantastic', 'wonderful', 'cheerful', 'cheery', 'well', 'upbeat']
feelings_negative = ['sad', 'nervous', 'stress', 'stressed', 'stressful', 'worried',
                     'anxious', 'scared', 'fearful', 'annoyed', 'bothered',
                     'terrible', 'horrible', 'awful', 'depressed', 'lonely',
                     'disgusted', 'crazy', 'insane', 'been better', 'down', 'dumps',
                     'confused', 'tired', 'grumpy', 'bad']
feelings_neutral = ['fine', 'ok', 'okay']
downers = ['death', 'dying', 'die', 'died', 'divorce', 'divorced', 'injury', 'hurt', 'injured', 'broke', 'broken'
           'fired', 'lost', 'imprisoned']
uppers = ['married', 'marriage', 'marry', 'promote', 'promotion', 'a raise', 'birth', 'new baby', 'fun']
negative = ['no', 'nope', 'absolutely not', 'of course not']
negation = ['didnt', 'did not', 'dont', 'do not', 'not']

arcs = []

arcs.extend([(f, 'feelings_positive', 'type') for f in feelings_positive])
arcs.extend([(f, 'feelings_negative', 'type') for f in feelings_negative])
arcs.extend([(f, 'feelings_neutral', 'type') for f in feelings_neutral])
arcs.extend([(f, 'downers', 'type') for f in downers])
arcs.extend([(f, 'uppers', 'type') for f in uppers])
arcs.extend([(f, 'negative', 'type') for f in negative])
arcs.extend([(f, 'positive_indicators', 'type') for f in positive_indicators])
arcs.extend([(f, 'negative_indicators', 'type') for f in negative_indicators])
arcs.extend([(f, 'negation', 'type') for f in negation])
arcs.extend([])
for arc in arcs:
    component.knowledge_base().add(*arc)


component.add_transition(
    'prestart', 'how_are_you',
    None, ["how are you"]
)

component.add_transition(
    'how_are_you', 'feeling_pos',
    '&feelings_positive',
    ["im good"]
)

component.add_transition(
    'how_are_you', 'feeling_neg',
    '&feelings_negative',
    ["im bad"]
)

component.add_transition(
    'how_are_you', 'feeling_neutral',
    '&feelings_neutral',
    ["im ok"]
)

component.add_transition(
    'how_are_you', 'unrecognized_emotion',
    None,
    ["im trying"],
    settings = 'e'
)

component.add_transition(
    'how_are_you', 'decline_share',
    '{'
    '({dont, do not, cant, cannot, shouldnt, should not}, {talk, discuss, share}),'
    '&negative'
    '}',
    ["i dont want to talk about it"]
)

component.add_transition(
    'unrecognized_emotion', 'end',
    None,
    ["Hmm, I'm not sure what you mean."],
    settings = 'e'
)

component.add_transition(
    'feeling_pos', 'acknowledge_pos',
    None,
    ["Im glad to hear that. What has caused your good mood?"]
)

component.add_transition(
    'feeling_neg', 'acknowledge_neg',
    None,
    ["Im sorry thats how you feel today. If you don't mind talking about it, what happened?"]
)

component.add_transition(
    'feeling_neutral', 'acknowledge_neutral',
    None,
    ["That's understandable. Is there anything in particular that made you feel this way?"]
)

# expand REGEX
component.add_transition(
    'acknowledge_pos', 'share_pos',
    '{'
    '(-{didnt, did not, dont, do not, not}, &positive_indicators),'
    '}',
    ["i just had a good day with my family yesterday"]
)

component.add_transition(
    'acknowledge_neg', 'share_pos',
    '{'
    '(-{didnt, did not, dont, do not, not}, &positive_indicators),'
    '}',
    ["i just had a good day with my family yesterday"]
)

component.add_transition(
    'acknowledge_neutral', 'share_pos',
    '{'
    '(-{didnt, did not, dont, do not, not}, &positive_indicators),'
    '}',
    ["i just had a good day with my family yesterday"]
)

component.add_transition(
    'acknowledge_pos', 'share_neg',
    '&negative_indicators',
    ["i didnt sleep well last night"]
)

component.add_transition(
    'acknowledge_neg', 'share_neg',
    '&negative_indicators',
    ["i didnt sleep well last night"]
)

component.add_transition(
    'acknowledge_neutral', 'share_neg',
    '&negative_indicators',
    ["i didnt sleep well last night"]
)

component.add_transition(
    'acknowledge_pos', 'decline_share',
    '{'
    '({dont, do not, cant, cannot, shouldnt, should not}, {talk, discuss, share}),'
    '&negative'
    '}',
    ["i dont want to talk about it"]
)

component.add_transition(
    'acknowledge_neg', 'decline_share',
    '{'
    '({dont, do not, cant, cannot, shouldnt, should not}, {talk, discuss, share}),'
    '&negative'
    '}',
    ["i dont want to talk about it"]
)

component.add_transition(
    'acknowledge_neutral', 'decline_share',
    '{'
    '({dont, do not, cant, cannot, shouldnt, should not}, {talk, discuss, share}),'
    '&negative'
    '}',
    ["i dont want to talk about it"]
)

component.add_transition(
    'acknowledge_pos', 'misunderstood',
    None,
    ["just stuff"],
    settings = 'e'
)

component.add_transition(
    'acknowledge_neg', 'misunderstood',
    None,
    ["just stuff"],
    settings = 'e'
)

component.add_transition(
    'acknowledge_neutral', 'misunderstood',
    None,
    ["just stuff"],
    settings = 'e'
)

component.add_transition(
    'misunderstood', 'end',
    None,
    ["Thanks for sharing that with me."]
)

component.add_transition(
    'share_pos', 'acknowledge_share_pos',
    None,
    ["Sounds really nice, thanks for sharing that with me. I love hearing about your life."]
)

component.add_transition(
    'share_neg', 'acknowledge_share_neg',
    None,
    ["I think that sounds really unfortunate, I hope it gets better for you soon."]
)

component.add_transition(
    'decline_share', 'acknowledge_decline_share',
    None,
    ["That's ok, I'm happy to talk about other things too."]
)

component.add_transition(
    'acknowledge_share_pos', 'end',
    None,
    ["thats cool"]
)

component.add_transition(
    'acknowledge_share_neg', 'end',
    None,
    ["thats cool"]
)

component.add_transition(
    'acknowledge_decline_share', 'end',
    None,
    ["thats cool"]
)

component.add_transition(
    'garbage', 'end',
    None, ['thats cool']
)

component.add_transition(
    'end', 'end', None, ['x'], settings='e'
)

if __name__ == '__main__':
    print(component.system_transition())
    i = input('U: ')
    while True:
        arg_dict = {"prev_conv_date": "2019-12-20 16:55:33.562881", "name": "sarah"}
        arg_dict2 = {"prev_conv_date": "2019-12-12 16:55:33.562881", "name": "sarah"}
        arg_dict3 = {"prev_conv_date": None, "stat": "Ive met quite a few people with your name recently."}
        if i == "hello":
            arg_dict["request_type"] = "LaunchRequest"
            arg_dict2["request_type"] = "LaunchRequest"
            arg_dict3["request_type"] = "LaunchRequest"
        confidence = component.user_transition(i, arg_dict) / 10 - 0.3
        print(component.state(), component.vars())
        if component.state() == "end":
            break
        component.vars().update({key:val for key,val in arg_dict.items() if val is not None})
        print('({}) '.format(confidence), component.system_transition())
        if component.state() == "end":
            break
        i = input('U: ')