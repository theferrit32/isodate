import re
from six import string_types
from isodate.isoerror import ISO8601Error
from isodate.isodatetime import parse_datetime, datetime_isoformat
from isodate.isodates import parse_date, date_isoformat
from isodate.isotime import parse_time, time_isoformat
from isodate.isoduration import parse_duration

from isodate.isostrf import (strftime, D_DEFAULT, DATE_EXT_COMPLETE, TIME_EXT_COMPLETE,
    TZ_EXT, DT_EXT_COMPLETE, D_ALT_EXT)
from isodate.interval import Interval

from datetime import datetime, time, date, timedelta

SEGMENT_DELIM = "/"
ISO8601_REPEAT_REGEX = re.compile(r"^R(?P<count>[0-9]*)$")


def parse_interval(interval_string):
    if not isinstance(interval_string, string_types):
        raise TypeError("Expecing a string")

    segment_count = interval_string.count(SEGMENT_DELIM)
    if segment_count < 1 or segment_count > 2:
        raise ISO8601Error("Improper number of interval string segments. Must have 1 or 2")

    segments = interval_string.split(SEGMENT_DELIM)
    for idx, seg in enumerate(segments):
        if len(seg) == 0:
            return ISO8601Error("Interval segment index %s was empty" % idx)

    count = None
    if len(segments) == 3:
        # Rn/start/end
        # Rn/start/duration
        # Rn/duration/end
        s0 = segments[0]
        match = ISO8601_REPEAT_REGEX.match(s0)
        if not match:
            raise ISO8601Error("Repeat notation did not match expected")
        groups = match.groupdict()
        count = groups.get("count", None)
        if len(count) > 0:
            count = int(count)
        segments = segments[1:]

    s0 = segments[0]
    s1 = segments[1]
    # remaining segments are either
    # 1) start/end.
    #     start must be a fully specified datetime format
    #     end can either be a time, date, or datetime
    # 2) start/duration
    #     start must be a fully specified datetime format
    #     duration must be a valid duration format
    # 3) duration/end
    #     duration must be a valid duration format
    #     end must be a fully specified datetime format
    start = None
    end = None
    duration = None
    try: # (1)
        start = parse_datetime(s0)
        print("second to last term is a datetime")
    except:
        try:
            duration = parse_duration(s0)
            print("second to last term is a datetime")
        except:
            raise ISO8601Error("First term after repeat must be either "
                               + "a fully specified datetime or a valid duration")
    # look at last term
    # this isn't the prettiest way to do it, but it is effective
    # could also build the regexes from other modules, but delegation avoids code duplication
    if start:
        # last term must be a duration, date, time or datetime
        try:
            end = parse_datetime(s1)
            print("last term is a datetime")
        except:
            try:
                end = parse_date(s1)
                print("last term is a date")
            except:
                try:
                    end = parse_time(s1)
                    print("last term is a time")
                except:
                    try:
                        duration = parse_duration(s1)
                        print("last term is a duration")
                    except:
                        raise ISO8601Error(
                                "When first term after repeat is a datetime, "
                                + "last term must be either a duration, datetime, date, or time")
    elif duration:
        # last term must be the end datetime
        try:
            end = parse_datetime(s1)
        except:
            raise ISO8601Error("If first term after repeat is a duration, "
                               + "last term must be a datetime")

    interval = Interval(start=start, end=end, duration=duration, repeat=count)
    print(interval)

"""
Let user pass two objects, and optional repeat, and a format.
arg1 must be either a datetime.datetime or a datetime.timedelta
  1. if arg1 is a datetime, arg2 must be either a datetime, time, date, or duration.
  2. if arg1 is a duration, arg2 must be a datetime

fmt:
  If None, attempt to auto-detect based on values of arg1, arg2, and repeat.

  Can be 2 or 3 slash separated segments. If there are 3 segments, the first segment
  is interpreted as a repeat.  The repeat must be either "R" or "Rn".

  If a repeat argument is specified but not in the fmt string, it will be left out.
  If a repeat argument is not provided or is None, but repeat is in the fmt string,
  the repeat in the output string will be set to infinite repeat, regardless of
  the inclusion of "n" in the repeat format.

  The remaining 2 fmt segments are interpreted based on the type of arg1 and arg2, and
  applied respectively.
"""

INTERVAL_FMT_DT_DUR = DT_EXT_COMPLETE + "/" + D_ALT_EXT
INTERVAL_FMT_R_DT_DUR = "Rn/" + INTERVAL_FMT_DT_D

INTERVAL_FMT_DT_DATE = DT_EXT_COMPLETE + "/" + DATE_EXT_COMPLETE
INTERVAL_FMT_R_DT_DATE = "Rn/" + INTERVAL_FMT_DT_DATE

INTERVAL_FMT_DT_TIME = DT_EXT_COMPLETE + "/" + TIME_EXT_COMPLETE
INTERVAL_FMT_R_DT_TIME = "Rn/" + INTERVAL_FMT_DT_TIME

INTERVAL_FMT_DT_DT = DT_EXT_COMPLETE + "/" + DT_EXT_COMPLETE
INTERVAL_FMT_R_DT_DT = "Rn/" + INTERVAL_FMT_DT_DT

INTERVAL_FMT_DUR_DT = D_ALT_EXT + "/" + DT_EXT_COMPLETE
INTERVAL_FMT_R_DUR_DT = "Rn/" + INTERVAL_FMT_DUR_DT

def interval_isoformat(arg1, arg2, repeat=None, fmt=None):
    output_r = output_1 = output_2 = None

    # check format
    fmt_segments = [None, None, None]
    if fmt:
        fmt_segments = fmt.split("/")
        if len(fmt_segments) == 3:
            r_fmt = fmt_segments[0]
            # only allow R or Rn
            if r_fmt == "R":
                output_r = "R"
            if r_fmt == "Rn":
                output_r = "R"
                if repeat:
                    if not isinstance(repeat, (int, long)) or repeat < 0:
                        raise TypeError("repeat must be an whole, non-negative number")
                    output_r += repeat

            # remove repeat format and proceed with other 2 arg formatting
            fmt_segments = fmt_segments[1:]
    else:
        if repeat:
            output_r = "R"
    if isinstance(arg1, datetime):
        str_1 = datetime_isoformat(arg1, fmt_segments[0])
        #assert (isinstance(arg2, datetime, time, date, timedelta))
        if isinstance(arg2, datetime):
            str_2 = datetime_isoformat(arg2, format=fmt_segments[1])
        elif isinstance(arg2, date):
            str_2 = date_isoformat(arg2, format=fmt_segments[1])
    elif isinstance(arg1, datetime.timedelta):
        str1 = duration_isoformat(arg1)
        #assert (isinstance(arg2, datetime))
    else:
         raise ISO8601Error("arg1 must be a datetime, time, date, or timedelta object")
