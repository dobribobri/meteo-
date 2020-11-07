# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from __future__ import division
from __future__ import print_function
from typing import Union, Tuple
from pythonlangutil.overload import Overload, signature
from datetime import datetime, date, timedelta
import math
import numpy as np

BEGIN_OF_TIME_BORLAND = date(1899, 12, 30)
BEGIN_OF_TIME_CPP = date(1900, 1, 1)

END_OF_DAY = {'hh': 23, 'mm': 59, 'ss': 59, 'ms': 999}

coeffs = {'hh': 0.041666667, 'mm': 0.000694444, 'ss': 0.000011574, 'ms': 0.000000012}


def Double2TDateTime(double: float, date_0: date = BEGIN_OF_TIME_BORLAND) -> 'TDateTime':
    fractionalPart, integerPart = math.modf(double)
    DATE = date_0 + timedelta(days=integerPart)

    hh = fractionalPart // coeffs['hh']
    if hh == 24:
        hh = 23
    fractionalPart -= hh / 24
    if fractionalPart < 0:
        return TDateTime(DATE.year, DATE.month, DATE.day,
                         int(hh), mm=0, ss=0, ms=0, date_0=date_0)

    mm = fractionalPart // coeffs['mm']
    if mm == 60:
        mm = 59
    fractionalPart -= mm / 1440
    if fractionalPart < 0:
        return TDateTime(DATE.year, DATE.month, DATE.day,
                         int(hh), int(mm), ss=0, ms=0, date_0=date_0)

    ss = fractionalPart // coeffs['ss']
    if ss == 60:
        ss = 59
    fractionalPart -= ss / 86400
    if fractionalPart < 0:
        return TDateTime(DATE.year, DATE.month, DATE.day,
                         int(hh), int(mm), int(ss), ms=0, date_0=date_0)

    ms = np.round(fractionalPart / coeffs['ms'])
    if ms == 1000:
        ms = 999
    return TDateTime(DATE.year, DATE.month, DATE.day,
                     int(hh), int(mm), int(ss), int(ms), date_0=date_0)


def daterange(start_date: 'TDateTime', stop_date: 'TDateTime'):
    """
    :param start_date: Borland format.
    :param stop_date: Borland format.
    :return: Range of dates as instances of Python "date" class.
    """
    start_date = start_date.toPythonDate()
    stop_date = stop_date.toPythonDate()
    for n in range(int((stop_date - start_date).days) + 1):
        yield start_date + timedelta(n)


class TDateTime:
    def __init__(self, YYYY: Union[int, str] = 1899, MM: Union[int, str] = 12, DD: Union[int, str] = 30,
                 hh: Union[int, str] = 0, mm: Union[int, str] = 0, ss: Union[int, str] = 0, ms: Union[int, str] = 0,
                 date_0: date = BEGIN_OF_TIME_BORLAND):
        self.DD, self.MM, self.YYYY, self.hh, self.mm, self.ss, self.ms = \
            int(DD), int(MM), int(YYYY), int(hh), int(mm), int(ss), int(ms)
        self.date_0 = date_0

    def toPythonDate(self) -> date:
        return date(self.YYYY, self.MM, self.DD)

    @staticmethod
    def fromPythonDate(Date: date) -> 'TDateTime':
        return TDateTime(Date.year, Date.month, Date.day)

    def toPythonDateTime(self) -> datetime:
        return datetime(self.YYYY, self.MM, self.DD, self.hh, self.mm, self.ss, self.ms*1000)

    @staticmethod
    def fromPythonDateTime(DT: datetime) -> 'TDateTime':
        return TDateTime(DT.year, DT.month, DT.day, DT.hour, DT.minute, DT.second, int(DT.microsecond/1000))

    def toDouble(self) -> float:
        integerPart = abs((self.toPythonDate() - self.date_0).days)
        fractionalPart = (self.hh * 0.041666667 + self.mm * 0.000694444 +
                          self.ss * 0.000011574 + self.ms * 0.000000012)
        value = integerPart + fractionalPart
        return value

    @staticmethod
    def fromDouble(double: float) -> 'TDateTime':
        return Double2TDateTime(double)

    def copy(self) -> 'TDateTime':
        return TDateTime(self.DD, self.MM, self.YYYY, self.hh, self.mm, self.ss, self.ms, self.date_0)

    def strDate(self, year=True, month=True, day=True) -> str:
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
    def strTime(self, hours: bool, minutes: bool, seconds: bool, milliseconds: bool) -> str:
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
    @signature()
    def strTime(self) -> str:
        return self.strTime(True, True, True, True)

    @strTime.overload
    @signature('str')
    def strTime(self, timeformat: str) -> str:
        return self.strTime(*TDateTime.timeformat_parser(timeformat))

    def strSeconds(self) -> str:
        return str(self.hh * 3600 + self.mm * 60 + self.ss + int(np.round(self.ms/1000)))

    def __str__(self):
        out = datetime(self.YYYY, self.MM, self.DD, self.hh, self.mm, self.ss)
        ms = "%.0f" % self.ms
        ms = '{0:0>3}'.format(ms)
        return out.strftime("%d.%m.%Y %H:%M:%S") + ' ' + ms

    @staticmethod
    def timeformat_parser(timeformat: str) -> Tuple[bool, bool, bool, bool]:
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

    def set(self, YYYY: Union[int, str] = None, MM: Union[int, str] = None, DD: Union[int, str] = None,
            hh: Union[int, str] = None, mm: Union[int, str] = None, ss: Union[int, str] = None,
            ms: Union[int, str] = None, date_0: date = None) -> None:
        if YYYY:
            self.YYYY = YYYY
        if MM:
            self.MM = MM
        if DD:
            self.DD = DD
        if hh:
            self.hh = hh
        if mm:
            self.mm = mm
        if ss:
            self.ss = ss
        if ms:
            self.ms = ms
        if date_0:
            self.date_0 = date_0
