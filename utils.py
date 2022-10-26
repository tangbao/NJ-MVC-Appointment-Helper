import pytz
from datetime import datetime
from datetime import timezone, timedelta
import json
from lxml import etree
import yaml

from const import *


def load_secret(logger=None):
    with open("config.secret.yaml", 'r') as stream:
        try:
            secret = yaml.safe_load(stream)
            secret['admin'] = str(secret['admin'])
            secret['authorized users'] = [str(x) for x in secret['authorized users']]
        except yaml.YAMLError as exc:
            if logger is not None:
                logger.error(exc)
            exit(1)
    return secret


def load_auth_users(logger=None):
    with open("config.secret.yaml", 'r') as stream:
        try:
            secret = yaml.safe_load(stream)
            secret['authorized users'] = [str(x) for x in secret['authorized users']]
        except yaml.YAMLError as exc:
            if logger is not None:
                logger.error(exc)
            exit(1)
    return secret['authorized users']


def is_dst(dt=None, timezone="UTC"):
    if dt is None:
        dt = datetime.utcnow()
    timezone = pytz.timezone(timezone)
    timezone_aware_date = timezone.localize(dt, is_dst=None)
    return timezone_aware_date.tzinfo._dst.seconds != 0


def dt_to_ts(dt):
    if is_dst(dt, timezone='US/Eastern'):
        return dt.replace(tzinfo=timezone(timedelta(hours=-4))).timestamp()
    else:
        return dt.replace(tzinfo=timezone(timedelta(hours=-5))).timestamp()


def is_valid_date(date_str):
    if date_str == '0' or date_str == 'All':
        return True

    try:
        dt = datetime.strptime(date_str, '%y%m%d')
    except ValueError:
        return False

    return not is_expired_date(date_str)


# check if the subscription (job) has expired
def is_expired_date(date_str):
    dt = datetime.strptime(date_str, '%y%m%d')
    ts = dt_to_ts(dt) + 86400  # the end of day
    return ts < datetime.now().timestamp()


# if job_date < target_date, return true; else return false
def compare_date(job_date, last_time):
    last_time_dt = datetime.strptime(last_time, '%y%m%d')
    return dt_to_ts(job_date) <= dt_to_ts(last_time_dt) + 86400


def parse_response_all(response, last_time, list_len):
    dom = etree.HTML(response.text)
    try:
        js_content = str(dom.xpath('/html/body/script[22]/text()')[0])
    except IndexError:
        return []
    else:
        time_data = js_content.split('\r\n')[2][23:]
        try:
            time_data_list_raw = json.loads(time_data)
        except json.decoder.JSONDecodeError:
            return []
        else:
            time_data_list = []
            for item in time_data_list_raw:
                time = item['FirstOpenSlot'][-19:]
                if time == "ointments Available":
                    continue
                time_fmt = datetime.strptime(time, '%m/%d/%Y %I:%M %p')
                if compare_date(time_fmt, last_time):
                    time_data_list.append({
                        'LocationId': item['LocationId'],
                        'FirstOpenSlot': time_fmt
                    })
            sorted_list = sorted(time_data_list, key=lambda e: e.__getitem__('FirstOpenSlot'))

            return sorted_list[:list_len]


def parse_response_one(response, last_time, loc_id):
    dom = etree.HTML(response.text)
    try:
        time_raw = str(dom.xpath('/html/body/main/div/div[2]/div/div/div/div[3]/div/div[2]/div/a/@href')[0]).split('/')
    except IndexError:
        return []
    else:
        time = time_raw[-2] + ' ' + time_raw[-1]
        time_fmt = datetime.strptime(time, '%Y-%m-%d %H%M')
        return_time = []
        if compare_date(time_fmt, last_time):
            return_time.append({
                    'LocationId': loc_id,
                    'FirstOpenSlot': time_fmt
                })
        return return_time


def gen_avail_places(sorted_list, service_time_url, is_from_parse_one):
    if len(sorted_list) == 0:
        return "No places available for the service you are querying. Please check later."

    reply = 'The most recent {:d} places you can visit: (date in yyyy-mm-dd, time in 24H)\n\n'.format(len(sorted_list))

    for item in sorted_list:
        reply = reply + 'Time: ' + str(item['FirstOpenSlot']) + '\n' \
                + 'Location: ' + LOCATION_ID[str(item['LocationId'])] + ' (' \
                + LOCATION_ID_ADDR[str(item['LocationId'])] + ')\n' \
                + 'Link: ' + service_time_url + '/'
        if not is_from_parse_one:
            reply = reply + str(item['LocationId']) + '\n\n'
        else:
            reply = reply + '\n\n'
    return reply


def gen_job_list_keyboard(job_len):
    job_list_keyboard = [[], ['0'], ['/cancel']]
    for i in range(job_len):
        job_list_keyboard[0].append(str(i + 1))
    return job_list_keyboard
