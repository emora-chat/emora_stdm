
from emora_stdm import DialogueFlow
from emora_stdm.state_transition_dialogue_manager import natex_common as natexes
import os
from copy import deepcopy

df = DialogueFlow(initial_state="system_root", kb=os.path.join('modules','family.json'))


'''
birthday_friend: told user friend's bday is coming
birthday_friend_gift: told user planned gift
birthday_friend_gift_rec: planned gift to get friend
birthday_friend_no_help: user is not helping emora

'''

flow = {
    'state': 'system_root',

    '"Oh, did i tell you? My friend\'s birthday is coming up. I\'m thinking of getting her a music box. What do you think, is it a good gift?"'
    '#GATE(birthday_friend:None) #SET($birthday_friend=True, $birthday_friend_gift=music box)': {
        'state': 'initial_gift_suggestion',

        'error': {
            'state': 'gift_suggestion',
            'hop': True
        },
        '{' + natexes.agree + ', [#EXP(positive_sentiment)]}': {
            'score': 1.1,
            '"Wow, you made up your mind so quickly. But I\'m still not sure... How do you know my friend will like it?"': {
                'state': 'gift_suggestion',
                'error': {
                    '[!#GATE() {"Yeah. I just want to get her something she really likes.",'
                    '"Sure. I\'m really hoping to surpise her with a great gift.",'
                    '"Yeah. I just hope she likes whatever I get her"}]': 'gift_suggestion',

                    '#GATE() "Yeah. So, what do you think I should get my friend for her birthday?"':{
                        'error': 'gift_suggestion',
                    },
                    '"Sure. You know, after talking with you I think I\'ve made up my mind to get my friend the music box after all. Thanks for your help."': 'end'
                },
                '[what, you, {get, buy, give}]':{
                    '"Well like I said, I was thinking of getting her a music box. But, I\'m not sure."': 'gift_suggestion'
                },
                '<she, just, friend>':{
                    '"Yeah she\'s my friend, I\'ve known her about a year."': 'gift_suggestion'
                },
                '[i, {"don\'t" know, not sure, no idea, dont}]': {
                    '#GATE() "Well neither do I! Please help me"': 'gift_suggestion',
                    '"Well if you\'re not sure, I think I\'ll get her the music box."': {
                        'state': 'end',
                        'score': 0.9
                    }
                },
                '[name]': {
                    '"Her name is Shannon."': 'gift_suggestion'
                },
                '[{old, age}]': {
                    '"She\'s turning twenty."': 'gift_suggestion'
                },
                '[!{[what, box], what is that, [what, does, {it, box} do]}]': {
                    '"It\'s a small box, and when you open it, it plays a beautiful melody."': 'gift_suggestion'
                },
                '[!#GATE(birthday_friend_gift:music box) [how, work]]': {
                    '"I\'m not sure how music boxes are made, but it\'s an interesting question"': 'gift_suggestion'
                },
                '<{like, listen, enjoy, into} {music}>': {
                    '"She loves all kinds of music! We talk about it all the time together, so I thought getting her a music box would be nice."': 'gift_suggestion'
                },
                '[birthday]': {
                    '"Yeah her birthday is exactly one week from today, she\'s turning twenty."': 'gift_suggestion'
                },
                '[{get, gotten}, {her, Shannon}, {last year, before, past}]': {
                    '"Well, last year I got her... Umm... Last year I got her a music box"': {
                        'error': {
                            '"Yes, I already got her a music box! That\'s why I need your help! Please, help me choose something to get her."': 'gift_suggestion'
                        }
                    }
                },
                '[ask, {her, Shannon, friend}]': {
                    '"I can\'t ask her! I want it to be a surprise!"': 'gift_suggestion'
                },
                '{ok, okay, sure, fine, alright, "dont\'t worry", [{I, "I\'ll"} help]}': {
                    '"Thank you for helping me. So, what do you think I should do?"': 'gift_suggestion'
                },
                '<{music box, music boxes} #EXP(postive_sentiment)>': {
                    '"Yeah, I thought it would be kind of unique. So I should get the music box for her?"': {
                        'error':{
                            'state': 'gift_suggestion',
                            'hop': True
                        },
                        natexes.agree:{
                            '"That\'s great! I\'ll get it for her then. Thanks so much for your help!"': 'end'
                        },
                        natexes.disagree:{
                            '"Oh okay, well what should I get then?"': 'gift_suggestion'
                        }
                    }
                },
                '[what, {she, Shannon, friend} {like, into, want, wants, likes, get herself, need, needs}]': {
                    '"Well, she likes music, and she\'s kind of artistic. I think she would appreciate something unique and personal."': 'gift_suggestion'
                },
                '[{does, did, would}, {she, Shannon, friend}, {like, into, enjoy, want, need, ask for}, {music box, box}]': {
                    '"I don\'t know if she wants a music box, that\'s why I need your help!"': 'gift_suggestion'
                },
                '[{you, your, "you\'re"}, #EXP(negative_sentiment), friend]': {
                    '"What? I\'m a good friend! I\'m really trying to do something thoughtful here!"': 'gift_suggestion'
                },
                '{[how long, you, {friend, her, Shannon}], <{are you, is she}, close>}': {
                    '"I don\'t know, I guess we\'re pretty close. I\'ve maybe known her a year?"': 'gift_suggestion'
                },
                natexes.question: {
                    'score': 0.1,
                    '{"I don\'t know." "Hmm.. I\'m not sure."}'
                    ' {"I really need your help though.", "But I need help,"} {"What should I do?", "What do you think I should get her?"}': 'gift_suggestion'
                },
                '[!#GATE(birthday_friend_gift:music box) #NOT(#EXP(negation)) '
                '{[{she will, "she\'ll", she would, friend would, friend will, Shannon will, Shannon would} {like, love, want, need}, {it, box}],'
                '[{give, get, buy, go for, music} {it, box}]'
                '[she will]'
                '[{i, "i\'m"}, {know, sure}]}]': {
                    'score': 1.1,
                    'state': 'gift_thanks',
                    '"Okay, well, if you\'re sure, then I\'ll get her the music box! '
                    'I think she\'ll appreciate how unique it is as a gift. Thanks so much for helping me!"': 'end'
                },
                '{[!a /.*/] [{get, buy, give, gift} {her, friend, Shannon}]}':{
                    'score': 0.2,
                    '"Hmm.. I\'m just not sure that\'s the right gift for my friend."': 'gift_suggestion',
                    '"Oh okay, yeah! I\'ll give her that as a gift! Thank you for helping me"':{
                        'state': 'end',
                        'score': 0.1
                    }
                },
                '[$birthday_friend_gift=#ONTE(gift_item)]':{
                    'state': 'alternate_suggestion',

                    '#ISP($birthday_friend_gift)'
                    '"Hmm" $birthday_friend_gift '
                    '{". Not a bad idea.", ". That\'s a good thought", ". Good idea"}'
                    '{"You think she\'ll like them?", "You really think my friend will like them?"}':{
                        natexes.agree:{
                            '"Okay, well, if you\'re sure, then I\'ll get her" $birthday_friend_gift "! Thanks so much for helping me!"': 'end'
                        },
                        natexes.disagree: {
                            '"Ok, well, what do you think then? What should I get my friend?"': 'gift_suggestion'
                        },
                        'error':{
                            'state': 'gift_suggestion',
                            'hop': True
                        }
                    },
                    '#NOT(#ISP($birthday_friend_gift))'
                    '"Hmm" $birthday_friend_gift '
                    '{". Not a bad idea.", ". That\'s a good thought", ". Good idea"}'
                    '{"You think she\'ll like it?", "You really think my friend will like it?"}':{
                        natexes.agree:{
                            '"Okay, well, if you\'re sure, then I\'ll get her a" $birthday_friend_gift "! Thanks so much for helping me!"': 'end'
                        },
                        natexes.disagree: {
                            '"Ok, well, what do you think then? What should I get my friend?"': 'gift_suggestion'
                        },
                        'error':{
                            'state': 'gift_suggestion',
                            'hop': True
                        }
                    }

                }
            }
        },
        natexes.disagree:{
            'score': 1.2,
            '"Oh alright. Well, what do you think I should get her?"': {
                'error': 'gift_suggestion'
            }
        },
        '[$birthday_friend_gift=#ONTE(item)]':{
            'state': 'alternate_suggestion',
            'score': 1.3
        }

    }
}

df.load_transitions(flow)
df.precache_transitions()

if __name__ == '__main__':

    df.run(debugging=False)

































