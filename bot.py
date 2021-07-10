import logging

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

from const import *


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


SERVICE_CHOICE, LOCATION_CHOICE = range(2)


def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['KNOWLEDGE TESTING']]

    update.message.reply_text(
        'Welcome to use this bot for NJ MVC appointment check. \n\n'
        'Send /cancel to stop at any time.\n\n'
        'What service do you want to make an appointment?\n'
        'Only KNOWLEDGE TESTING is supported now.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Services'
        ),
    )
    return SERVICE_CHOICE


def service_time_check(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s chooses %s", user.first_name, update.message.text)
    service_time_url = URL + service_code[update.message.text]
    response = requests.get(service_time_url)
    dom = etree.HTML(response.text)
    js_content = str(dom.xpath('/html/body/script[22]/text()')[0])
    time_data = js_content.split('\r\n')[2][23:]
    update.message.reply_text(time_data)
    update.message.reply_text('Bye!')
    return ConversationHandler.END


def location_time_check(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s want to check location time", user.first_name)
    update.message.reply_text('check the time of a location is underconstruction')
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the service.", user.first_name)
    update.message.reply_text(
        'Bye!', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Echo is on for testing: '+update.message.text)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, the command does not support.")


def main() -> None:
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SERVICE_CHOICE: [MessageHandler(Filters.regex('^(KNOWLEDGE TESTING)$'), service_time_check)],
            LOCATION_CHOICE: [MessageHandler(Filters.text & ~Filters.command, location_time_check)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(conv_handler)

    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
