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
CANCEL_JOB = 0


def start(update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to use this bot for NJ MVC appointment check. \n\n' + HELP_MSG)


def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(HELP_MSG)


def check(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s starts to check time.", user.first_name)

    update.message.reply_text(
        CHECK_MSG,
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
    update.message.reply_text('Blah blah blah. I don\'t understand what you\'re talking about.')


def unknown(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, the command does not support.")


def auth_check_subscribe(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s starts to subscribe.", user.first_name)
    if str(user.id) not in AUTHORIZED_USERS:
        update.message.reply_text(NO_AUTH_MSG)
        return ConversationHandler.END
    else:
        if len(context.job_queue.jobs()) >= JOB_LIMIT:
            update.message.reply_text('Sorry, you have too many subscriptions. Please use /mysub to cancel some first.')
            return ConversationHandler.END

        update.message.reply_text(
            CHECK_MSG,
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
    update.message.reply_text('Good. You subscribe to ' + update.message.text + '.\n\n' + SET_LOC_MSG,
                              reply_markup=ReplyKeyboardMarkup(
                                  [['All']], one_time_keyboard=True, input_field_placeholder='Locations'
                              ))

    return TIME_SELECT


def time_select(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    location = update.message.text
    logger.info("User %s chooses %s", user.first_name, location)

    service_id = SERVICE_ID[context.user_data.get('SERVICE')]
    if location not in LOCATION_NAME[service_id].keys() and \
            location not in LOCATION_NAME[service_id].values() and location != 'All':
        update.message.reply_text('Sorry, location not found. Please try again.\n\n' + SET_LOC_MSG,
                                  reply_markup=ReplyKeyboardMarkup(
                                      [['All']], one_time_keyboard=True, input_field_placeholder='Locations'
                                  ))
        return TIME_SELECT

    if location == 'All':
        context.user_data["LOCATION_ID"] = '0'
    elif location in LOCATION_ID.keys():
        context.user_data["LOCATION_ID"] = location
    else:
        context.user_data["LOCATION_ID"] = [k for k, v in LOCATION_NAME[service_id].items() if v == location][0]

    update.message.reply_text('Please tell me the last date you can accept to do the business in MVC.\n\n' +
                              TME_FMT_MSG,
                              reply_markup=ReplyKeyboardMarkup(
                                  [['All']], one_time_keyboard=True, input_field_placeholder='Time'
                              ))

    return CONFIRM_INFO


def confirm_info(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    time = update.message.text
    logger.info("User %s chooses %s", user.first_name, time)

    if not is_valid_date(time):
        update.message.reply_text('Error: Wrong time format.\n\n' + TME_FMT_MSG,
                                  reply_markup=ReplyKeyboardMarkup(
                                      [['All']], one_time_keyboard=True, input_field_placeholder='Time'
                                  ))
        return CONFIRM_INFO
    else:
        if time == 'All':
            time = '331231'
        context.user_data['TIME'] = time
        update.message.reply_text('You are subscribing to ' + context.user_data.get('SERVICE', 'NOT FOUND') +
                                  ' at ' + LOCATION_ID[context.user_data.get('LOCATION_ID')] +
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
        # todo: need to modify when subscribe to only one place
        result = parse_response(response, 1)
        if len(result) == 1:
            context.bot.send_message(chat_id=detail['CHAT_ID'],
                                     text=gen_avail_places(result, detail['SERVICE_URL']))
        else:
            logger.error('No available place found.')


def job_reg(update: Update, context: CallbackContext) -> int:
    job = {
        'CHAT_ID': update.message.chat_id,
        'SERVICE': context.user_data.get('SERVICE'),
        'LOCATION_ID': context.user_data.get('LOCATION_ID'),
        'TIME': context.user_data.get('TIME'),
    }

    job['SERVICE_URL'] = MVC_URL + SERVICE_ID[job['SERVICE']]
    name = job['TIME'] + ' (date in yymmdd), ' + LOCATION_ID[job['LOCATION_ID']] + ' (location), ' + job['SERVICE']
    job['NAME'] = name
    context.job_queue.run_repeating(appt_check, interval=300, first=10, name=name, context=job)
    context.user_data.clear()
    update.message.reply_text('Your subscription ' + name + ' is scheduled successfully.',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def auth_check_sublist(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s starts to check subscription list.", user.first_name)
    if str(user.id) not in AUTHORIZED_USERS:
        update.message.reply_text(NO_AUTH_MSG)
        return ConversationHandler.END
    else:
        jobs = context.job_queue.jobs()
        if len(jobs) == 0:
            update.message.reply_text('You have no running subscriptions.')
            return ConversationHandler.END
        else:
            update.message.reply_text('Here are the running subscriptions you have.')
            for i in range(len(jobs)):
                update.message.reply_text(str(i+1) + ': ' + jobs[i].name)
            update.message.reply_text(SET_JOB_MSG,
                                      reply_markup=ReplyKeyboardMarkup(
                                        gen_job_list_keyboard(len(jobs)),
                                        one_time_keyboard=True, input_field_placeholder='mysubs'
                                      ))
            return CANCEL_JOB


def cancel_job(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    job_idx = update.message.text
    logger.info("User %s starts to cancel job %s.", user.first_name, job_idx)
    jobs = context.job_queue.jobs()
    jobs_str_list = [str(x+1) for x in list(range(len(jobs)))]

    if job_idx not in jobs_str_list:
        update.message.reply_text('Invalid subscription index.\n\n'+SET_JOB_MSG,
                                  reply_markup=ReplyKeyboardMarkup(
                                      gen_job_list_keyboard(len(jobs)),
                                      one_time_keyboard=True, input_field_placeholder='mysubs'
                                  ))
        return CANCEL_JOB

    if job_idx == '0':
        for job in jobs:
            job.schedule_removal()
            logger.info(job.name + ' removed')
        update.message.reply_text('All subscriptions canceled!', reply_markup=ReplyKeyboardRemove())
    else:
        job = jobs[int(job_idx)-1]
        job.schedule_removal()
        logger.info(job.name + ' removed')
        update.message.reply_text(job.name + ' canceled!', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


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
        entry_points=[CommandHandler('subscribe', auth_check_subscribe)],
        states={
            LOCATION_SELECT: [MessageHandler(Filters.text & (~Filters.command), location_select)],
            TIME_SELECT: [MessageHandler(Filters.text & (~Filters.command), time_select)],
            CONFIRM_INFO: [MessageHandler(Filters.text & (~Filters.command), confirm_info)],
            JOB_REG: [CommandHandler('confirm', job_reg)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    sublist_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('mysub', auth_check_sublist)],
        states={
            CANCEL_JOB: [MessageHandler(Filters.text & (~Filters.command), cancel_job)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(check_conv_handler)
    dispatcher.add_handler(subscribe_conv_handler)
    dispatcher.add_handler(sublist_conv_handler)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), usr_msg))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
