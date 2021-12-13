import logging
import html
import traceback

import requests

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    ParseMode,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    Defaults,
)

from const import *
from utils import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

config = load_config(logger)

SERVICE_TIME = 0
LOCATION_SELECT, TIME_SELECT, CONFIRM_INFO, JOB_REG = range(4)
CANCEL_JOB = 0


def start(update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to use this bot for NJ MVC appointment check. \n\n' + HELP_MSG)
    update.message.reply_text(TEST_NEED_MSG)


def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(HELP_MSG)
    update.message.reply_text(TEST_NEED_MSG)


def global_cancel(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    logger.info("User %s chooses global cancel", user.full_name)
    context.user_data.clear()
    update.message.reply_text(
        'There is no on-going conversation session to be canceled. If you want to cancel a subscription, please use '
        '/mysub', reply_markup=ReplyKeyboardRemove()
    )


def check(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s starts to check time.", user.full_name)
    update.message.reply_text(TEST_NEED_MSG)

    update.message.reply_text(
        CHECK_MSG,
        reply_markup=ReplyKeyboardMarkup(
            SERVICE_KEYBOARD, one_time_keyboard=True, input_field_placeholder='Services'
        ),
    )
    return SERVICE_TIME


def service_time_check(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s chooses %s", user.full_name, update.message.text)

    if update.message.text not in SERVICE_ID.keys():
        update.message.reply_text('Sorry, service not found. Please try again.')
        return SERVICE_TIME

    service_time_url = MVC_URL + SERVICE_ID[update.message.text]
    update.message.reply_text('You are querying the available locations for ' + update.message.text + '.\n' +
                              'You can visit ' + service_time_url + ' directly for all available locations.\n' +
                              'It may take some time to get the results because NJ MVC website is unstable.',
                              reply_markup=ReplyKeyboardRemove())
    try:
        response = requests.get(service_time_url, timeout=config['timeout'])
    except Exception:
        logger.error('Fail to connect to NJ MVC website.')
        update.message.reply_text(
            'Error: cannot connect to the NJ MVC website. Please try again later.'
        )
        return ConversationHandler.END
    else:
        sorted_time_list = parse_response_all(response, '331231', 3)
        update.message.reply_text(gen_avail_places(sorted_time_list, service_time_url, is_from_parse_one=False))
        update.message.reply_text('Thank you for using. Bye!')
        return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the service.", user.full_name)
    context.user_data.clear()
    update.message.reply_text(
        'Session ends. Bye!', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def usr_msg(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    logger.info("User %s said: %s", user.full_name, update.message.text)
    update.message.reply_text('Blah blah blah. I don\'t understand what you\'re talking about.')


def unknown(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, the command does not support.")


def get_usr_jobs(context, uid):
    jobs = context.job_queue.jobs()
    usr_jobs = []
    for job in jobs:
        if job.context['CHAT_ID'] == uid:
            usr_jobs.append(job)
    return usr_jobs


def auth_check_subscribe(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s starts to subscribe.", user.full_name)
    if config['require auth'] and str(user.id) not in config['authorized users']:
        update.message.reply_text(NO_AUTH_MSG)
        update.message.reply_text(TEST_NEED_MSG)
        return ConversationHandler.END
    else:
        if len(get_usr_jobs(context, user.id)) >= config['job limit']:
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
    logger.info("User %s chooses %s", user.full_name, update.message.text)

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
    logger.info("User %s chooses %s", user.full_name, location)

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
    logger.info("User %s chooses %s", user.full_name, time)

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
                                  'appointments every ' + str(config['query interval']) + ' seconds, and send you a '
                                  'notification when one is available.\n\n'
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
                                 text='You subscription ' + detail['NAME'] + ' has expired. Please start a new one.\n\n'
                                 'If you received no messages from the bot, it could because there was no available'
                                 'places found by the bot.')
        job.schedule_removal()
    try:
        response = requests.get(detail['SERVICE_URL'], timeout=config['timeout'])
    except:
        logger.error('Fail to connect to NJ MVC website.')
    else:
        if detail['LOCATION_ID'] == '0':
            result = parse_response_all(response, detail['TIME'], 1)
            is_from_parse_one = False
        else:
            result = parse_response_one(response, detail['TIME'], detail['LOCATION_ID'])
            is_from_parse_one = True
        if len(result) == 1:
            context.bot.send_message(chat_id=detail['CHAT_ID'],
                                     text=gen_avail_places(result, detail['SERVICE_URL'], is_from_parse_one))
            logger.info('Find one and send to ' + str(detail['CHAT_ID']))
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
    if job['LOCATION_ID'] != '0':
        job['SERVICE_URL'] = job['SERVICE_URL'] + '/' + job['LOCATION_ID']
    name = job['TIME'] + ' (date in yymmdd), ' + LOCATION_ID[job['LOCATION_ID']] + ' (location), ' + job['SERVICE']
    job['NAME'] = name
    context.job_queue.run_repeating(appt_check, interval=config['query interval'], first=10, name=name, context=job)
    context.user_data.clear()
    update.message.reply_text('Your subscription ' + name + ' is scheduled successfully.',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def auth_check_sublist(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s starts to check subscription list.", user.full_name)

    if config['require auth'] and str(user.id) not in config['authorized users']:
        update.message.reply_text(NO_AUTH_MSG)
        return ConversationHandler.END
    else:
        jobs = get_usr_jobs(context, user.id)
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
    logger.info("User %s starts to cancel job %s.", user.full_name, job_idx)
    jobs = get_usr_jobs(context, user.id)
    jobs_str_list = [str(x) for x in list(range(len(jobs)+1))]

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


def update_config(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    logger.info("User %s starts to update authorized user list.", user.full_name)

    if str(user.id) != config['admin']:
        update.message.reply_text('You do not have the admin privilege to do so.')
    else:
        globals()['config'] = load_config(logger)
        update.message.reply_text('Configs updated successfully!')


def error_handler(update: object, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the admin."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    context.bot.send_message(chat_id=config['admin'], text=message[:4096], parse_mode=ParseMode.HTML)


def main() -> None:
    default = Defaults(disable_web_page_preview=True)

    if config['test mode']:
        token = config['test token']
    else:
        token = config['token']

    updater = Updater(token=token, use_context=True, defaults=default)
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
    dispatcher.add_handler(CommandHandler('cancel', global_cancel))
    dispatcher.add_handler(CommandHandler('updateconfig', update_config))

    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), usr_msg))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
