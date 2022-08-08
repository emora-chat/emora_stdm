
from emora_stdm import DialogueFlow

chat_quad = {
    'state' : 'quad', #can scan qr here
    '"The Quad(rangle) is the original and historical part of the Atlanta campus. It\'s a great place to hang out after class!"':{
        '[something else random, emory history]':{
            'state': 'emory_history1',
            '"Emory was founded in 1836 in Oxford, GA and we still maintain this original campus! Emory College moved to Atlanta and restarted its campus in 1915."':{
                '[{tell me more}]':{
                    'state' : 'emory_history2',
                    '"This was made possible by a gift from the founder of the Coca-Cola Company, Asa Griggs Candler. Candler\'s gift was $1 million and 72 acres of land in Druid Hills, GA - which is where we are now!"':{
                        'error' : 'start'
                    }
                },
                'error' : 'emory_history2'
            }
        },
        'error': 'emory_history1'
    }
}

chatbot = DialogueFlow('quad')
chatbot.load_transitions(chat_quad)
chatbot.run()