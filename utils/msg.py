from utils.const import *

CHECK_MSG = 'Send /cancel to stop at any time.\n\n' + \
            'What service do you want to make an appointment?\n'

SET_LOC_MSG = 'Please tell me the preferred MVC location you want to subscribe. ' + \
              'Please check ' + LOCATION_LIST_URL + ' for location names and ids.\n\n' + \
              'Either location id or location name is ' + \
              'supported.\n\n ' + \
              'If you have no preferred MVC location and want ' + \
              'to subscribe to all locations, ' + \
              'please reply All.'

TME_FMT_MSG = 'The format is yymmdd (US Eastern Time), e.g., 210704 means July 4th, 2021.\n\n' + \
              'If you have no requirements on this, please reply All.'

NO_AUTH_MSG = 'Sorry, you are not the authorized user, you cannot use this function.\n\n' + \
              'Instead, you can deploy this bot by yourself.\n\n' + \
              'Please visit ' + PRJ_URL + ' for more information.'

SET_JOB_MSG = 'Reply the index of the subscription to cancel it. ' + \
              'Reply 0 to cancel all. \n\nSend /cancel to quit this procedure.'

HELP_MSG = '/check Check the most recent available places for appointment.\n' + \
           '/subscribe Receive a notification when a more recent time slot is available. Authorized users only. ' \
           'You can have at most three subscriptions.\n' + \
           '/mysub Manage your subscriptions.\n' + \
           '/help Show the help message.\n\n' + \
           'Visit ' + PRJ_URL + ' to find the source code of this bot and instructions to deploy your own bot.'

IN_DEMO_MSG = 'You are in DEMO mode. You cannot really use the /subscribe and /mysub command. The returns of these ' \
              'two commands are just for DEMO.'

TEST_NEED_MSG = 'If you want to be one of the authorized users of this bot that can subscribe to appointments ' \
                '(so that the bot can check the appointments automatically for you), ' \
                'please contact me at Telegram @kirov_dev. For now, this /subscribe function is not stable and needs ' \
                'some more uses to find bugs. \n\n' \
                '****************\n' \
                'You don\'t have to be a programmer, but just a normal user who can report bugs to me.\n' \
                '****************'
