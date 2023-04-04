import time
from datetime import datetime


TS_FORMAT = "%Y-%m-%d %H:%M:%S"
ts_now_seconds = round(time.time())
ts_now_fmt_utc = time.strftime(TS_FORMAT, time.gmtime(ts_now_seconds))
ts_now_fmt_local = time.strftime(TS_FORMAT, time.localtime(ts_now_seconds))


def fmt_ts_millis(millis, as_utc=False):
    """ Convert epoch milliseconds to string format """
    if not millis:
        return None
    return fmt_ts_seconds(round(millis/1000), as_utc)


def fmt_ts_seconds(seconds, as_utc=False):
    """ Convert epoch seconds to string format """
    if not seconds:
        return None
    if as_utc:
        ts = time.gmtime(seconds)
    else:
        ts = time.localtime(seconds)
    return time.strftime(TS_FORMAT, ts)


def utc_str_to_millis(sdt):
    """ Convert UTC string to epoch milliseconds. """
    return utc_str_to_seconds(sdt) * 1000


def utc_str_to_seconds(sdt):
    """ Convert UTC string to epoch seconds. """
    dt = datetime.fromisoformat(sdt)
    seconds = (dt - datetime(1970, 1, 1)).total_seconds()
    return seconds
