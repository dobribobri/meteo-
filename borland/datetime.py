# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from datetime import datetime, date, timedelta
import math
from pythonlangutil.overload import Overload, signature
import numpy as np

BEGIN_OF_TIME_BORLAND = date(1899, 12, 30)
BEGIN_OF_TIME_CPP = date(1900, 1, 1)


def Double2TDateTime(double, date_0=BEGIN_OF_TIME_BORLAND):
    fractionalPart, integerPart = math.modf(double)
    DATE = date_0 + timedelta(days=integerPart)

    hh = fractionalPart // 0.041666667
    if hh == 24:
        hh = 23
    fractionalPart -= hh / 24
    if fractionalPart < 0:
        return TDateTime(DATE.year, DATE.month, DATE.day,
                         int(hh), mm=0, ss=0, ms=0, date_0=date_0)

    mm = fractionalPart // 0.000694444
    if mm == 60:
        mm = 59
    fractionalPart -= mm / 1440
    if fractionalPart < 0:
        return TDateTime(DATE.year, DATE.month, DATE.day,
                         int(hh), int(mm), ss=0, ms=0, date_0=date_0)

    ss = fractionalPart // 0.000011574
    if ss == 60:
        ss = 59
    fractionalPart -= ss / 86400
    if fractionalPart < 0:
        return TDateTime(DATE.year, DATE.month, DATE.day,
                         int(hh), int(mm), int(ss), ms=0, date_0=date_0)

    ms = np.round(fractionalPart / 0.000000012)
    if ms == 1000:
        ms = 999
    return TDateTime(DATE.year, DATE.month, DATE.day,
                     int(hh), int(mm), int(ss), int(ms), date_0=date_0)


class TDateTime:
    def __init__(self, YYYY=1899, MM=12, DD=30,
                 hh=0, mm=0, ss=0, ms=0, date_0=BEGIN_OF_TIME_BORLAND):
        self.DD, self.MM, self.YYYY, self.hh, self.mm, self.ss, self.ms = \
            int(DD), int(MM), int(YYYY), int(hh), int(mm), int(ss), int(ms)
        self.date_0 = date_0

    @staticmethod
    def __days_between(d1, d2):
        return abs((d2 - d1).days)

    def toDouble(self):
        integerPart = TDateTime.__days_between(date(self.YYYY, self.MM, self.DD), self.date_0)
        fractionalPart = (self.hh * 0.041666667 + self.mm * 0.000694444 +
                          self.ss * 0.000011574 + self.ms * 0.000000012)
        value = integerPart + fractionalPart
        return value

    def fromDouble(self, double):
        return Double2TDateTime(double, self.date_0)

    def strDate(self, year=True, month=True, day=True):
        out = datetime(self.YYYY, self.MM, self.DD)
        fs = ''
        if day:
            fs += "%d"
        if month:
            if fs:
                fs += ":%m"
            else:
                fs += "%m"
        if year:
            if fs:
                fs += ":%Y"
            else:
                fs += "%Y"
        return out.strftime(fs)

    @Overload
    @signature('bool', 'bool', 'bool', 'bool')
    def strTime(self, hours=True, minutes=True, seconds=True, milliseconds=True):
        out = datetime(1899, 12, 30,
                       hour=self.hh, minute=self.mm, second=self.ss)
        ms = "%.0f" % self.ms
        ms = '{0:0>3}'.format(ms)
        fs = ''
        if hours:
            fs += "%H"
        if minutes:
            if fs:
                fs += ":%M"
            else:
                fs += "%M"
        if seconds:
            if fs:
                fs += ":%S"
            else:
                fs += "%S"
        result = out.strftime(fs)
        if milliseconds:
            result += ' ' + ms
        return result

    @strTime.overload
    @signature('str')
    def strTime(self, timeformat: str):
        return self.strTime(*TDateTime.timeformat_parser(timeformat))

    def strSeconds(self):
        return str(self.hh * 3600 + self.mm * 60 + self.ss)

    def __str__(self):
        out = datetime(self.YYYY, self.MM, self.DD, self.hh, self.mm, self.ss)
        ms = "%.0f" % self.ms
        ms = '{0:0>3}'.format(ms)
        return out.strftime("%d.%m.%Y %H:%M:%S") + ' ' + ms

    @staticmethod
    def timeformat_parser(timeformat: str):
        hours, minutes, seconds, milliseconds = False, False, False, False
        if 'h' in timeformat:
            hours = True
        if 'm' in timeformat:
            minutes = True
        if 's' in timeformat:
            seconds = True
        if '+' in timeformat:
            milliseconds = True
        return hours, minutes, seconds, milliseconds
