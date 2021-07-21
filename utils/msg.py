
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

HELP_MSG = '/check Check the most recent available places for appointment.\n' + \
           '/subscribe Receive a notification when a more recent time slot is available. Authorized users only.\n' + \
           '/help Show the help message.\n'
