
from emora_stdm import DialogueFlow

my_bot = DialogueFlow(initial_state='start', end_state='end')

my_bot.load_transitions({
  'state': 'start',
  '"Hello."': {
      '#INT(Hi! How are you?, How are you doing?)': {
          '"Good. How are you?"': {
              'state': 'asking-user-mood',

              '[{good, great, okay}]': {

                  '"That\'s great! ' 
                  'Know what\'s good about today?"': {
                        'error': 'weather-subconvo'
                  }
              },
              '{[bad, horrible, awful]}': {
                  '"Oh no! Bye!"': 'end'
              },
              'error': {
                  '"I do not understand! Bye!"': 'end'
              }
          }
      },
      '#INT(Tell me the weather.)': {
          'state': 'weather-subconvo',

          '"It is sunny out!"': {
              'error': {
                  '"Bye!"': 'end'
              }
          }
      }
  }
})

if __name__ == '__main__':
    my_bot.run()