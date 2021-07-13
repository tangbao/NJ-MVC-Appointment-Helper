import logging
import json
import datetime
import re

import requests
from lxml import etree
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

from utils.const import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

SERVICE_CHOICE, LOCATION_CHOICE = range(2)


def start(update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to use this bot for NJ MVC appointment check. \n\n' +
                              '/check Check the most recent available places for appointment.\n' +
                              '/subscribe Receive a notification when a more recent time slot is available. '
                              'Authorized users only.\n' +
                              '/help Show the help message.')


def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('/check Check the most recent available places for appointment.\n' +
                              '/subscribe Receive a notification when a more recent time slot is available. '
                              'Authorized users only.\n' +
                              '/help Show the help message.')


def check(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['INITIAL PERMIT (NOT FOR KNOWLEDGE TEST)', 'KNOWLEDGE TESTING', 'REAL ID'],
                      ['CDL PERMIT OR ENDORSEMENT - (NOT FOR KNOWLEDGE TEST)', 'NON-DRIVER ID'],
                      ['RENEWAL: LICENSE OR NON-DRIVER ID', 'RENEWAL: CDL', 'TRANSFER FROM OUT OF STATE'],
                      ['NEW TITLE OR REGISTRATION', 'SENIOR NEW TITLE OR REGISTRATION (65+)'],
                      ['REGISTRATION RENEWAL', 'TITLE DUPLICATE/REPLACEMENT']]

    update.message.reply_text(
        'Send /cancel to stop at any time.\n\n'
        'What service do you want to make an appointment?\n',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Services'
        ),
    )
    return SERVICE_CHOICE


def service_time_check(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s chooses %s", user.first_name, update.message.text)
    service_time_url = URL + service_code[update.message.text]
    update.message.reply_text('You are querying the available locations for ' + update.message.text + '.\n' +
                              'You can visit ' + service_time_url + ' directly for all available locations.\n' +
                              'It may take some time to get the results because NJ MVC website is unstable.')
    try:
        response = requests.get(service_time_url)
    except Exception:
        logger.error('Fail to connect to NJ MVC website.')
        update.message.reply_text(
            'Error: cannot connect to the NJ MVC website. Please try again later.', reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    else:
        sorted_time_list = parse_response(response)
        update.message.reply_text(gen_avail_places(sorted_time_list, service_time_url))
        update.message.reply_text(
            'Thank you for using. Bye!', reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END


def parse_response(response):
    dom = etree.HTML(response.text)
    js_content = str(dom.xpath('/html/body/script[22]/text()')[0])
    time_data = js_content.split('\r\n')[2][23:]
    time_data_list_raw = json.loads(time_data)
    time_data_list = []
    for item in time_data_list_raw:
        time = item['FirstOpenSlot'][-19:]
        if time == "ointments Available":
            continue
        time_fmt = datetime.datetime.strptime(time, '%m/%d/%Y %I:%M %p')
        time_data_list.append({
            'LocationId': item['LocationId'],
            'FirstOpenSlot': time_fmt
        })
    sorted_list = sorted(time_data_list, key=lambda e: e.__getitem__('FirstOpenSlot'))

    if len(sorted_list) < 3:
        return sorted_list
    else:
        return sorted_list[:3]


def gen_avail_places(sorted_list, service_time_url):
    if len(sorted_list) == 0:
        return "No places available for the service you are querying. Please check later."

    reply = 'The most recent {:d} places you can visit: (date in yyyy-mm-dd, time in 24H)\n\n'.format(len(sorted_list))
    for item in sorted_list:
        reply = reply + 'Location: ' + location_id[str(item['LocationId'])] + '\n' \
                + 'Time: ' + str(item['FirstOpenSlot']) + '\n' \
                + 'Link: ' + service_time_url + '/' + str(item['LocationId']) + '\n\n'
    return reply


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the service.", user.first_name)
    update.message.reply_text(
        'Bye!', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def usr_msg(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    logger.info("User %s said: %s", user.first_name, update.message.text)
    update.message.reply_text('blah blah blah')


def unknown(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, the command does not support.")


def service_choice_regex():
    regex = '^('
    for item in service_code.keys():
        regex = regex + re.escape(item) + '|'
    return regex[:-1] + ')$'


def main() -> None:
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('check', check)],
        states={
            SERVICE_CHOICE: [MessageHandler(Filters.regex(service_choice_regex()), service_time_check)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(conv_handler)

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    help_handler = CommandHandler('help', help)
    dispatcher.add_handler(help_handler)

    usr_msg_handler = MessageHandler(Filters.text & (~Filters.command), usr_msg)
    dispatcher.add_handler(usr_msg_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
