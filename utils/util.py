import pytz
from datetime import datetime
from datetime import timezone, timedelta


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
