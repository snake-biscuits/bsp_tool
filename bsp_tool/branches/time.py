from __future__ import annotations
import datetime
import enum

from . import base


class Month(enum.Enum):
    January = 1
    February = 2
    March = 3
    April = 4
    May = 5
    June = 6
    July = 7
    August = 8
    September = 9
    October = 10
    November = 11
    December = 12


class WeekDay(enum.Enum):
    Sunday = 0
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6


class SystemTime(base.MappedArray):
    # https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-systemtime
    year: int
    month: Month
    day_of_week: WeekDay
    day: int
    hour: int
    second: int
    millisecond: int
    _mapping = ["year", "month", "day_of_week", "day",
                "hour", "minute", "second", "millisecond"]
    _classes = {"month": Month}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert 1601 <= self.year <= 30827
        assert 1 <= self.day <= 31
        assert 0 <= self.hour <= 23
        assert 0 <= self.second <= 59  # what's a leap second lol
        assert 0 <= self.millisecond <= 999

    def __repr__(self) -> str:
        time_string = self.as_datetime().strftime("%Y/%m/%d (%a) %H:%M:%S.%f")
        return f"<{self.__class__.__name__} {time_string}>"

    def as_datetime(self) -> datetime.datetime:
        return datetime.datetime(self.year, self.month.value, self.day,
                                 self.hour, self.minute, self.second, self.millisecond * 1000)

    @classmethod
    def from_datetime(cls, dt: datetime.datetime) -> SystemTime:
        tuple_ = (dt.year, dt.month, dt.weekday() + 1, dt.day,
                  dt.hour, dt.minute, dt.second, dt.microsecond // 1000)
        return cls(*tuple_)

    @classmethod
    def now(cls) -> SystemTime:
        return cls.from_datetime(datetime.datetime.now())
