from isodate.isodatetime import datetime_isoformat
from isodate.isoduration import duration_isoformat


class Interval(object):
    """
    """


    """
    start: datetime.datetime
    duration: datetime.timedelta
    repeat: int
    """
    def __init__(self, start=None, end=None, duration=None, repeat=None):
        self.start = start
        self.end = end
        self.duration = duration
        self.repeat = repeat

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.dict.update(state)

    def __getattr__(self, name):
        pass
        #TODO

    def __str__(self):
        ret = ""
        if self.repeat:
            ret += "R%d/" % self.repeat
        if self.start and self.end:
            ret += "%s/%s" % (datetime_isoformat(self.start), datetime_isoformat(self.end))
        elif self.start and self.duration:
            ret += "%s/%s" % (datetime_isoformat(self.start), duration_isoformat(self.duration))
        elif self.duration and self.end:
            ret += "%s/%s" % (duration_isoformat(self.duration), datetime_isoformat(self.end))
        else:
            raise ISO8601Error("Could not produce a valid ISO8601 interval string")
        return ret


    def __repr__(self):
        #TODO
        pass

    def __hash__(self):
        return hash((self.start, self.end, self.duration, self.repeat))
