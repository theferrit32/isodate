import re
from six import string_types
from isodate.isoerror import ISO8601Error
from isodate.isodatetime import parse_datetime
from isodate.isodates import parse_date
from isodate.isotime import parse_time
from isodate.isoduration import parse_duration

from isodate.isostrf import strftime, D_DEFAULT
from isodate.interval import Interval

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
        segments = [segments[1], segments[2]]

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
