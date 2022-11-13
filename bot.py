import logging
from logging.handlers import TimedRotatingFileHandler
import html
import os.path
import traceback

import requests

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)

from telegram.constants import ParseMode

from telegram.ext import (
    filters,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    Defaults,
    ContextTypes
)

from const import *
from utils import *

SERVICE_TIME = 0
LOCATION_SELECT, TIME_SELECT, CONFIRM_INFO, JOB_REG = range(4)
CANCEL_JOB = 0


class NJMVCBot:
    def __init__(self, args):
        self.args = args
        self.logger = self.init_logging()
        self.config = self.init_config()
        self.init_bot()

    def init_logging(self):
        if not os.path.exists('./log'):
            os.makedirs('./log')
        logHandler = TimedRotatingFileHandler('./log/njmvcbot.log', when='D', interval=1, backupCount=7)
        logHandler.suffix = "%Y-%m-%d.log"

        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO,
                            handlers=[logHandler])
        return logging.getLogger(__name__)

    def init_config(self):
        config = load_secret(self.logger)
        config['test mode'] = self.args.test
        config['require auth'] = self.args.auth
        config['job limit'] = self.args.joblimit
        config['timeout'] = self.args.timeout
        config['query interval'] = self.args.qintvl
        return config

    def init_bot(self):
        if self.config['test mode']:
            token = self.config['test token']
        else:
            token = self.config['token']
        default = Defaults(disable_web_page_preview=True)

        application = ApplicationBuilder().token(token).defaults(default).build()
        check_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('check', self.check)],
            states={
                SERVICE_TIME: [MessageHandler(filters.TEXT & (~filters.COMMAND), self.service_time_check)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )

        subscribe_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('subscribe', self.auth_check_subscribe)],
            states={
                LOCATION_SELECT: [MessageHandler(filters.TEXT & (~filters.COMMAND), self.location_select)],
                TIME_SELECT: [MessageHandler(filters.TEXT & (~filters.COMMAND), self.time_select)],
                CONFIRM_INFO: [MessageHandler(filters.TEXT & (~filters.COMMAND), self.confirm_info)],
                JOB_REG: [CommandHandler('confirm', self.job_reg)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )

        sublist_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('mysub', self.auth_check_sublist)],
            states={
                CANCEL_JOB: [MessageHandler(filters.TEXT & (~filters.COMMAND), self.cancel_job)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )

        application.add_handler(check_conv_handler)
        application.add_handler(subscribe_conv_handler)
        application.add_handler(sublist_conv_handler)

        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CommandHandler('help', self.help))
        application.add_handler(CommandHandler('cancel', self.global_cancel))
        application.add_handler(CommandHandler('updateauthuser', self.update_auth_users))

        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.usr_msg))
        application.add_handler(MessageHandler(filters.COMMAND, self.unknown))

        application.add_error_handler(self.error_handler)

        application.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text('Welcome to use this bot for NJ MVC appointment check. \n\n' + HELP_MSG)
        await update.message.reply_text(TEST_NEED_MSG)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(HELP_MSG)
        await update.message.reply_text(TEST_NEED_MSG)

    async def global_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        self.logger.info("User %s chooses global cancel", user.full_name)
        context.user_data.clear()
        await update.message.reply_text(
                                        'There is no on-going conversation session to be canceled. '
                                        'If you want to cancel a subscription, please use '
                                        '/mysub', reply_markup=ReplyKeyboardRemove()
        )

    async def check(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        self.logger.info("User %s starts to check time.", user.full_name)
        await update.message.reply_text(TEST_NEED_MSG)

        await update.message.reply_text(
            CHECK_MSG,
            reply_markup=ReplyKeyboardMarkup(
                SERVICE_KEYBOARD, one_time_keyboard=True, input_field_placeholder='Services'
            ),
        )
        return SERVICE_TIME

    async def service_time_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        self.logger.info("User %s chooses %s", user.full_name, update.message.text)

        if update.message.text not in SERVICE_ID.keys():
            await update.message.reply_text('Sorry, service not found. Please try again.')
            return SERVICE_TIME

        service_time_url = MVC_URL + SERVICE_ID[update.message.text]
        await update.message.reply_text('You are querying the available locations for ' + update.message.text + '.\n' +
                                        'You can visit ' + service_time_url + ' directly for all available locations.\n'
                                        'It may take some time to get the results because NJ MVC website is unstable.',
                                        reply_markup=ReplyKeyboardRemove())
        try:
            response = requests.get(service_time_url, timeout=self.config['timeout'])
        except Exception:
            self.logger.error('Fail to connect to NJ MVC website.')
            await update.message.reply_text(
                'Error: cannot connect to the NJ MVC website. Please try again later.'
            )
            return ConversationHandler.END
        else:
            sorted_time_list = parse_response_all(response, '331231', 3)
            await update.message.reply_text(
                gen_avail_places(sorted_time_list, service_time_url, is_from_parse_one=False))
            await update.message.reply_text('Thank you for using. Bye!')
            return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        self.logger.info("User %s canceled the service.", user.full_name)
        context.user_data.clear()
        await update.message.reply_text(
            'Session ends. Bye!', reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    async def usr_msg(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        self.logger.info("User %s said: %s", user.full_name, update.message.text)
        await update.message.reply_text('Blah blah blah. I don\'t understand what you\'re talking about.')

    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, the command does not support.")

    def get_usr_jobs(self, context, uid):
        jobs = context.job_queue.jobs()
        usr_jobs = []
        for job in jobs:
            if job.data['CHAT_ID'] == uid:
                usr_jobs.append(job)
        return usr_jobs

    async def auth_check_subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        self.logger.info("User %s starts to subscribe.", user.full_name)
        if self.config['require auth'] and str(user.id) not in self.config['authorized users']:
            await update.message.reply_text(NO_AUTH_MSG)
            await update.message.reply_text(TEST_NEED_MSG)
            return ConversationHandler.END
        else:
            if len(self.get_usr_jobs(context, user.id)) >= self.config['job limit']:
                await update.message.reply_text(
                    'Sorry, you have too many subscriptions. Please use /mysub to cancel some first.')
                return ConversationHandler.END

            await update.message.reply_text(
                CHECK_MSG,
                reply_markup=ReplyKeyboardMarkup(
                    SERVICE_KEYBOARD, one_time_keyboard=True, input_field_placeholder='Services'
                ),
            )
            return LOCATION_SELECT

    async def location_select(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        self.logger.info("User %s chooses %s", user.full_name, update.message.text)

        if update.message.text not in SERVICE_ID.keys():
            await update.message.reply_text('Sorry, service not found. Please try again.')
            return LOCATION_SELECT

        context.user_data['SERVICE'] = update.message.text
        await update.message.reply_text('Good. You subscribe to ' + update.message.text + '.\n\n' + SET_LOC_MSG,
                                        reply_markup=ReplyKeyboardMarkup(
                                            [['All']], one_time_keyboard=True, input_field_placeholder='Locations'
                                        ))

        return TIME_SELECT

    async def time_select(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        location = update.message.text
        self.logger.info("User %s chooses %s", user.full_name, location)

        service_id = SERVICE_ID[context.user_data.get('SERVICE')]
        if location not in LOCATION_NAME[service_id].keys() and \
                location not in LOCATION_NAME[service_id].values() and location != 'All':
            await update.message.reply_text('Sorry, location not found. Please try again.\n\n' + SET_LOC_MSG,
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

        await update.message.reply_text('Please tell me the last date you can accept to do the business in MVC.\n\n' +
                                        TME_FMT_MSG,
                                        reply_markup=ReplyKeyboardMarkup(
                                            [['All']], one_time_keyboard=True, input_field_placeholder='Time'
                                        ))

        return CONFIRM_INFO

    async def confirm_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        time = update.message.text
        self.logger.info("User %s chooses %s", user.full_name, time)

        if not is_valid_date(time):
            await update.message.reply_text('Error: Wrong time format.\n\n' + TME_FMT_MSG,
                                            reply_markup=ReplyKeyboardMarkup(
                                                [['All']], one_time_keyboard=True, input_field_placeholder='Time'
                                            ))
            return CONFIRM_INFO
        else:
            if time == 'All':
                time = '331231'
            context.user_data['TIME'] = time
            await update.message.reply_text('You are subscribing to ' + context.user_data.get('SERVICE', 'NOT FOUND') +
                                            ' at ' + LOCATION_ID[context.user_data.get('LOCATION_ID')] +
                                            ' on or before ' + context.user_data.get('TIME', '331231') +
                                            ' (yymmdd).\n\n'
                                            'Reply /confirm to start the subscription. The bot will query available '
                                            'appointments every ' + str(self.config['query interval']) +
                                            ' seconds, and send you a '
                                            'notification when one is available.\n\n'
                                            'Reply /cancel to start a new subscribe if there\'s anything wrong.',
                                            reply_markup=ReplyKeyboardMarkup(
                                                [['/confirm', '/cancel']], one_time_keyboard=True,
                                                input_field_placeholder='y/n'
                                            ))
            return JOB_REG

    async def appt_check(self, context: ContextTypes.DEFAULT_TYPE):
        job = context.job
        detail = job.data
        if is_expired_date(detail['TIME']):
            await context.bot.send_message(chat_id=detail['CHAT_ID'],
                                           text='You subscription ' + detail['NAME'] +
                                                ' has expired. Please start a new one.\n\n'
                                                'If you received no messages from the bot, '
                                                'it could because there was no available'
                                                'places found by the bot.')
            job.schedule_removal()
        try:
            response = requests.get(detail['SERVICE_URL'], timeout=self.config['timeout'])
        except:
            self.logger.error('Fail to connect to NJ MVC website.')
        else:
            if detail['LOCATION_ID'] == '0':
                result = parse_response_all(response, detail['TIME'], 1)
                is_from_parse_one = False
            else:
                result = parse_response_one(response, detail['TIME'], detail['LOCATION_ID'])
                is_from_parse_one = True
            if len(result) == 1:
                await context.bot.send_message(chat_id=detail['CHAT_ID'],
                                               text=gen_avail_places(result, detail['SERVICE_URL'], is_from_parse_one))
                self.logger.info('Find one and send to ' + str(detail['CHAT_ID']))
            else:
                self.logger.error('No available place found.')

    async def job_reg(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
        context.job_queue.run_repeating(self.appt_check, interval=self.config['query interval'], first=10, name=name,
                                        data=job)
        context.user_data.clear()
        await update.message.reply_text('Your subscription ' + name + ' is scheduled successfully.',
                                        reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    async def auth_check_sublist(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        self.logger.info("User %s starts to check subscription list.", user.full_name)

        if self.config['require auth'] and str(user.id) not in self.config['authorized users']:
            await update.message.reply_text(NO_AUTH_MSG)
            return ConversationHandler.END
        else:
            jobs = self.get_usr_jobs(context, user.id)
            if len(jobs) == 0:
                await update.message.reply_text('You have no running subscriptions.')
                return ConversationHandler.END
            else:
                await update.message.reply_text('Here are the running subscriptions you have.')
                for i in range(len(jobs)):
                    await update.message.reply_text(str(i + 1) + ': ' + jobs[i].name)
                await update.message.reply_text(SET_JOB_MSG,
                                                reply_markup=ReplyKeyboardMarkup(
                                                    gen_job_list_keyboard(len(jobs)),
                                                    one_time_keyboard=True, input_field_placeholder='mysubs'
                                                ))
                return CANCEL_JOB

    async def cancel_job(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        job_idx = update.message.text
        self.logger.info("User %s starts to cancel job %s.", user.full_name, job_idx)
        jobs = self.get_usr_jobs(context, user.id)
        jobs_str_list = [str(x) for x in list(range(len(jobs) + 1))]

        if job_idx not in jobs_str_list:
            await update.message.reply_text('Invalid subscription index.\n\n' + SET_JOB_MSG,
                                            reply_markup=ReplyKeyboardMarkup(
                                                gen_job_list_keyboard(len(jobs)),
                                                one_time_keyboard=True, input_field_placeholder='mysubs'
                                            ))
            return CANCEL_JOB

        if job_idx == '0':
            for job in jobs:
                job.schedule_removal()
                self.logger.info(job.name + ' removed')
            await update.message.reply_text('All subscriptions canceled!', reply_markup=ReplyKeyboardRemove())
        else:
            job = jobs[int(job_idx) - 1]
            job.schedule_removal()
            self.logger.info(job.name + ' removed')
            await update.message.reply_text(job.name + ' canceled!', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    async def update_auth_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        self.logger.info("User %s starts to update authorized user list.", user.full_name)

        if str(user.id) != self.config['admin']:
            await update.message.reply_text('You do not have the admin privilege to do so.')
        else:
            self.config['authorized users'] = load_auth_users(self.logger)
            await update.message.reply_text('Authorized users updated successfully!')

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.logger.error(msg="Exception while handling an update:", exc_info=context.error)

        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)

        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        message = (
            f"An exception was raised while handling an update\n"
            f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
            "</pre>\n\n"
            f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
            f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
            f"<pre>{html.escape(tb_string)}</pre>"
        )

        await context.bot.send_message(
            chat_id=self.config['admin'], text=message[:4096], parse_mode=ParseMode.HTML
        )
