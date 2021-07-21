import logging

import requests

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

from utils.const import *
from utils.msg import *
from utils.util import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

SERVICE_TIME = 0
LOCATION_SELECT, TIME_SELECT, CONFIRM_INFO, JOB_REG = range(4)


def start(update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to use this bot for NJ MVC appointment check. \n\n' + HELP_MSG)


def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(HELP_MSG)


def check(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s starts to check time.", user.first_name)

    update.message.reply_text(
        'Send /cancel to stop at any time.\n\n'
        'What service do you want to make an appointment?\n',
        reply_markup=ReplyKeyboardMarkup(
            SERVICE_KEYBOARD, one_time_keyboard=True, input_field_placeholder='Services'
        ),
    )
    return SERVICE_TIME


def service_time_check(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s chooses %s", user.first_name, update.message.text)

    if update.message.text not in SERVICE_ID.keys():
        update.message.reply_text('Sorry, service not found. Please try again.')
        return SERVICE_TIME

    service_time_url = MVC_URL + SERVICE_ID[update.message.text]
    update.message.reply_text('You are querying the available locations for ' + update.message.text + '.\n' +
                              'You can visit ' + service_time_url + ' directly for all available locations.\n' +
                              'It may take some time to get the results because NJ MVC website is unstable.',
                              reply_markup=ReplyKeyboardRemove())
    try:
        response = requests.get(service_time_url)
    except Exception:
        logger.error('Fail to connect to NJ MVC website.')
        update.message.reply_text(
            'Error: cannot connect to the NJ MVC website. Please try again later.'
        )
        return ConversationHandler.END
    else:
        sorted_time_list = parse_response(response, 3)
        update.message.reply_text(gen_avail_places(sorted_time_list, service_time_url))
        update.message.reply_text('Thank you for using. Bye!')
        return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the service.", user.first_name)
    context.user_data.clear()
    update.message.reply_text(
        'Session ends. Bye!', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def usr_msg(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    logger.info("User %s said: %s", user.first_name, update.message.text)
    update.message.reply_text('blah blah blah')


def unknown(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, the command does not support.")


def auth_check(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s starts to subscribe.", user.first_name)
    if str(user.id) not in AUTHORIZED_USERS:
        update.message.reply_text('Sorry, you are not the authorized user, you cannot use this function.\n\n'
                                  'Instead, you can deploy this bot by yourself.\n\n'
                                  'Please visit ' + PRJ_URL + ' for more information.')
        return ConversationHandler.END
    else:
        update.message.reply_text(
            'Send /cancel to stop at any time.\n\n'
            'What service do you want to make an appointment?',
            reply_markup=ReplyKeyboardMarkup(
                SERVICE_KEYBOARD, one_time_keyboard=True, input_field_placeholder='Services'
            ),
        )
        return LOCATION_SELECT


def location_select(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s chooses %s", user.first_name, update.message.text)

    if update.message.text not in SERVICE_ID.keys():
        update.message.reply_text('Sorry, service not found. Please try again.')
        return LOCATION_SELECT

    context.user_data['SERVICE'] = update.message.text
    update.message.reply_text('Good. You subscribe to ' + update.message.text + '.\n\n'
                              'Please tell me the preferred MVC location you want to subscribe. '
                              'Please check ' + LOCATION_LIST_URL + ' for location names and ids.\n\n'
                                                                  'Either location id or location name is '
                                                                  'supported.\n\n '
                                                                  'If you have no preferred MVC location and want '
                                                                  'to subscribe to all locations, '
                                                                  'please reply 0 or All.',
                              reply_markup=ReplyKeyboardMarkup(
                                  [['All']], one_time_keyboard=True, input_field_placeholder='Locations'
                              ))

    return TIME_SELECT


def time_select(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    location = update.message.text
    logger.info("User %s chooses %s", user.first_name, location)

    if location not in LOCATION_ID.keys() and location not in LOCATION_ID.values():
        update.message.reply_text('Sorry, location not found. Please try again.\n\n'
                                  'Please check ' + LOCATION_LIST_URL + ' for location names and ids.\n\n'
                                                                      'Either location id or location name is '
                                                                      'supported.\n\n '
                                                                      'If you have no preferred MVC location and want '
                                                                      'to subscribe to all locations, '
                                                                      'please reply 0 or All.',
                                  reply_markup=ReplyKeyboardMarkup(
                                      [['All']], one_time_keyboard=True, input_field_placeholder='Locations'
                                  ))
        return TIME_SELECT

    if location in LOCATION_ID.keys():
        context.user_data["LOCATION_ID"] = location
    else:
        context.user_data["LOCATION_ID"] = [k for k, v in LOCATION_ID.items() if v == location][0]

    update.message.reply_text('Please tell me the last date you can accept to do the business in MVC.\n\n'
                              'The format is yymmdd (US Eastern Time), e.g., 210704 means July 4th, 2021.\n\n'
                              'If you have no requirements on this, please reply 0 or All.',
                              reply_markup=ReplyKeyboardMarkup(
                                  [['All']], one_time_keyboard=True, input_field_placeholder='Time'
                              ))

    return CONFIRM_INFO


def confirm_info(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    time = update.message.text
    logger.info("User %s chooses %s", user.first_name, time)

    if not is_valid_date(time):
        update.message.reply_text('Error: Wrong time format.\n\n'
                                  'The format is yymmdd (US Eastern Time), e.g., 210707 means July 7th, 2021.\n\n'
                                  'If you have no requirements on this, please reply 0 or All.',
                                  reply_markup=ReplyKeyboardMarkup(
                                      [['All']], one_time_keyboard=True, input_field_placeholder='Time'
                                  ))
        return CONFIRM_INFO
    else:
        if time == '0' or time == 'All':
            time = '331231'
        context.user_data['TIME'] = time
        update.message.reply_text('You are subscribing to ' + context.user_data.get('SERVICE', 'NOT FOUND') +
                                  ' at ' + LOCATION_ID[context.user_data.get('LOCATION_ID', '0')] +
                                  ' on or before ' + context.user_data.get('TIME', '331231') + ' (yymmdd).\n\n'
                                  'Reply /confirm to start the subscription. The bot will query available '
                                  'appointments every 5 min, and send you a notification when one is available.\n\n'
                                  'Reply /cancel to start a new subscribe if there\'s anything wrong.',
                                  reply_markup=ReplyKeyboardMarkup(
                                      [['/confirm', '/cancel']], one_time_keyboard=True, input_field_placeholder='y/n'
                                  ))
        return JOB_REG


def appt_check(context: CallbackContext):
    job = context.job
    detail = job.context
    print(detail['TIME'])
    if is_expired_date(detail['TIME']):
        context.bot.send_message(chat_id=detail['CHAT_ID'],
                                 text='You subscription ' + detail['name'] + ' has expired. Please start a new one.\n\n'
                                 'If you received no messages from the bot, it could because there was no available'
                                 'places found by the bot.')
        job.schedule_removal()
    try:
        response = requests.get(detail['SERVICE_URL'])
    except:
        logger.error('Fail to connect to NJ MVC website.')
    else:
        result = parse_response(response, 1)
        if len(result) == 1:
            context.bot.send_message(chat_id=detail['CHAT_ID'],
                                     text=gen_avail_places(result, detail['SERVICE_URL']))
        else:
            logger.error('No available place found.')


def job_reg(update: Update, context: CallbackContext) -> int:
    job = {
        'CHAT_ID': update.message.chat_id,
        'SERVICE': context.user_data.get('SERVICE', 'NOT FOUND'),
        'LOCATION_ID': context.user_data.get('LOCATION_ID', '0'),
        'TIME': context.user_data.get('TIME', '331231'),
    }

    if job['SERVICE'] == 'NOT FOUND':
        update.message.reply_text('ERROR: INVALID SERVICE', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    job['SERVICE_URL'] = MVC_URL + SERVICE_ID[job['SERVICE']]
    name = job['TIME'] + ', ' + LOCATION_ID[job['LOCATION_ID']] + ', ' + job['SERVICE']
    job['NAME'] = name
    context.job_queue.run_repeating(appt_check, interval=300, first=10, name=name, context=job)
    context.user_data.clear()
    update.message.reply_text('Your subscription ' + name + ' is scheduled successfully.',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def cancel_all_job(update: Update, context: CallbackContext) -> None:
    jobs = context.job_queue.jobs()
    for job in jobs:
        job.schedule_removal()
        print(job.name + ' removed')
    update.message.reply_text('All subscriptions canceled!', reply_markup=ReplyKeyboardRemove())


def main() -> None:
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    check_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('check', check)],
        states={
            SERVICE_TIME: [MessageHandler(Filters.text & (~Filters.command), service_time_check)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    subscribe_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('subscribe', auth_check)],
        states={
            LOCATION_SELECT: [MessageHandler(Filters.text & (~Filters.command), location_select)],
            TIME_SELECT: [MessageHandler(Filters.text & (~Filters.command), time_select)],
            CONFIRM_INFO: [MessageHandler(Filters.text & (~Filters.command), confirm_info)],
            JOB_REG: [CommandHandler('confirm', job_reg)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(check_conv_handler)
    dispatcher.add_handler(subscribe_conv_handler)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('cancelall', cancel_all_job))
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), usr_msg))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
