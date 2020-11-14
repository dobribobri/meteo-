# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from pythonlangutil.overload import Overload, signature
import os
from datetime import datetime
from session import Session
from borland_datetime import TDateTime, END_OF_DAY, daterange
from wparser import WFile
from settings import parameter as p


class Weather:
    @Overload
    @signature('float', 'float')
    def __init__(self, start_t: float, stop_t: float = None):
        self.initialized = False
        self.start_t = start_t
        self.stop_t = stop_t
        self.wfiles = []

        self.start = TDateTime.fromDouble(start_t)
        if stop_t:
            self.stop = TDateTime.fromDouble(stop_t)
        else:
            self.stop = self.start.copy()
            self.stop.set(**END_OF_DAY)
            self.stop_t = self.stop.toDouble()
        for d in daterange(self.start, self.stop):
            wfile = WFile.fromDate(d)
            if not os.path.exists(wfile.wdatapath):
                continue
            self.wfiles.append(wfile)

        self.DATA = Session()

    @__init__.overload
    @signature('TDateTime', 'TDateTime')
    def __init__(self, start: TDateTime, stop: TDateTime = None):
        start_t = start.toDouble()
        stop_t = None
        if stop:
            stop_t = stop.toDouble()
        self.__init__(start_t, stop_t)

    @__init__.overload
    @signature('datetime', 'datetime')
    def __init__(self, start: datetime, stop: datetime = None):
        start_d = TDateTime.fromPythonDateTime(start)
        stop_d = None
        if stop:
            stop_d = TDateTime.fromPythonDateTime(stop)
        self.__init__(start_d, stop_d)

    def apply(self, formatstr: str = 'tkmphrw*') -> None:
        self.DATA = self.getData(formatstr)

    def getData(self, formatstr: str = 'tkmphrw*') -> Session:
        """
        :param formatstr:
        Type 't' to get Temperature (Cels), 'k' to get Temperature (K), 'p' - Pressure (hPa), 'm' - Pressure (mmHg),
        'h' - relative humidity (%), 'r' - absolute humidity (g/m3), 'w' - wind speed (m/s),
        '*' - precipitation amount (mm). Example: 'tprw*'.

        :return: Session of weather data.
        """
        WDATA = Session()
        for wfile in self.wfiles:
            wfile.parse()
            wfile.cutData(self.start_t, self.stop_t)
            for char in formatstr:
                if char == 't':
                    WDATA.add(wfile.WDATA.get_series(p.weather.labels.T_C))
                if char == 'k':
                    WDATA.add(wfile.WDATA.get_series(p.weather.labels.T_K))
                if char == 'm':
                    WDATA.add(wfile.WDATA.get_series(p.weather.labels.P_mm))
                if char == 'p':
                    WDATA.add(wfile.WDATA.get_series(p.weather.labels.P_hpa))
                if char == 'h':
                    WDATA.add(wfile.WDATA.get_series(p.weather.labels.rho_rel))
                if char == 'r':
                    WDATA.add(wfile.WDATA.get_series(p.weather.labels.rho_abs))
                if char == 'w':
                    WDATA.add(wfile.WDATA.get_series(p.weather.labels.Vwind))
                if char == '*':
                    WDATA.add(wfile.WDATA.get_series(p.weather.labels.RainRt))
        WDATA.time_sorting()
        return WDATA

    def cutData(self, start_t: float, stop_t: float) -> None:
        self.DATA.cut(start_t, stop_t)

    def getInfo(self, timestamp: float) -> list:
        return self.DATA.get_spectrum(timestamp)

    def Pressure(self, timestamp: float, dimension: str = p.weather.labels.P_mm) -> float:
        return self.DATA.get_series(key=dimension).get(timestamp).val

    def Temperature(self, timestamp: float, dimension: str = p.weather.labels.T_C) -> float:
        return self.DATA.get_series(key=dimension).get(timestamp).val

    def Rho_rel(self, timestamp: float) -> float:
        return self.DATA.get_series(key=p.weather.labels.rho_rel).get(timestamp).val

    def Rho_abs(self, timestamp: float) -> float:
        return self.DATA.get_series(key=p.weather.labels.rho_abs).get(timestamp).val

    def WindV(self, timestamp: float) -> float:
        return self.DATA.get_series(key=p.weather.labels.Vwind).get(timestamp).val

    def RainRt(self, timestamp: float) -> float:
        return self.DATA.get_series(key=p.weather.labels.RainRt).get(timestamp).val
