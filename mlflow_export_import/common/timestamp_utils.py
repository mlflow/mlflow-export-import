import time


TS_FORMAT = "%Y-%m-%d %H:%M:%S"
ts_now_seconds = round(time.time())
ts_now_fmt_utc = time.strftime(TS_FORMAT, time.gmtime(ts_now_seconds))
ts_now_fmt_local = time.strftime(TS_FORMAT, time.localtime(ts_now_seconds))


def get_now_nice(as_utc=False):
    return fmt_ts_seconds(round(time.time()), as_utc)


def fmt_ts_millis(millis, as_utc=False):
    return fmt_ts_seconds(round(millis/1000), as_utc)


def fmt_ts_seconds(seconds, as_utc=False):
    ts_format = "%Y-%m-%d %H:%M:%S"
    if as_utc:
        ts = time.gmtime(seconds)
    else:
        ts = time.localtime(seconds)
    return time.strftime(ts_format, ts)
