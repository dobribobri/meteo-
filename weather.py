# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

import os
from datetime import date, timedelta
from collections import defaultdict
from borland.datetime import TDateTime, Double2TDateTime
from wparser import WFile


class Weather:
    def __init__(self, start_t: float = None, stop_t: float = None):
        self.initialized = False
        self.start_t = start_t
        self.stop_t = stop_t
        if start_t:
            self.start = Double2TDateTime(start_t)
            start_date = date(self.start.YYYY, self.start.MM, self.start.DD)
            if stop_t:
                self.stop = Double2TDateTime(stop_t)
            else:
                self.stop = TDateTime(self.start.YYYY, self.start.MM, self.start.DD,
                                      hh=23, mm=59, ss=59, ms=999)
                self.stop_t = self.stop.toDouble()
            stop_date = date(self.stop.YYYY, self.stop.MM, self.stop.DD)
            self.wfiles = []
            swp_tbl = WFile.load_swprop()
            for d in Weather.__daterange(start_date, stop_date):
                wfile = WFile(d.year, d.month, d.day)
                if not os.path.exists(wfile.wdatapath):
                    continue
                wfile.parse()
                wfile.set_swp_tbl(swp_tbl)
                self.wfiles.append(wfile)
            self.initialized = True

    def getWeatherDATA(self, formatstr: str = ''):
        WDATA = defaultdict(list)
        if not self.initialized:
            return WDATA
        frmtd = {'temper': 0, 'pressu': 0, 'rhorel': 0,
                 'rhoabs': 0, 'v_wind': 0, 'rainrt': 0}
        y = 0
        for char in formatstr:
            y += 1
            if char == 't':
                frmtd['temper'] = y
            if char == 'p':
                frmtd['pr_hpa'] = y
            if char == 'm':
                frmtd['mmrtst'] = y
            if char == 'h':
                frmtd['rhorel'] = y
            if char == 'r':
                frmtd['rhoabs'] = y
            if char == 'w':
                frmtd['v_wind'] = y
            if char == '*':
                frmtd['rainrt'] = y
        frmtd = sorted(frmtd.items(), key=lambda x: x[1])
        for wfile in self.wfiles:
            wfile.cutWDATA(self.start_t, self.stop_t)
            for key, val in frmtd:
                if val and (key == 'temper'):
                    for timestamp in wfile.WDATA.keys():
                        WDATA[key].append((timestamp, wfile.WDATA[timestamp][1]))
                if val and (key == 'mmrtst'):
                    for timestamp in wfile.WDATA.keys():
                        WDATA[key].append((timestamp, wfile.WDATA[timestamp][0]))
                if val and (key == 'pr_hpa'):
                    for timestamp in wfile.WDATA.keys():
                        WDATA[key].append((timestamp, wfile.Pressure(timestamp, dimension='hpa')))
                if val and (key == 'rhorel'):
                    for timestamp in wfile.WDATA.keys():
                        WDATA[key].append((timestamp, wfile.WDATA[timestamp][2]))
                if val and (key == 'rhoabs'):
                    for timestamp in wfile.WDATA.keys():
                        WDATA[key].append((timestamp, wfile.Rho_abs(timestamp)))
                if val and (key == 'v_wind'):
                    for timestamp in wfile.WDATA.keys():
                        WDATA[key].append((timestamp, wfile.WDATA[timestamp][3]))
                if val and (key == 'rainrt'):
                    for timestamp in wfile.WDATA.keys():
                        WDATA[key].append((timestamp, wfile.WDATA[timestamp][4]))
        return WDATA

    @staticmethod
    def __daterange(start_date, stop_date):
        for n in range(int((stop_date - start_date).days) + 1):
            yield start_date + timedelta(n)

    def __get(self, timestamp: float):
        if not self.initialized:
            self.__init__(start_t=timestamp)
        for wfile in self.wfiles:
            if wfile.min_t <= timestamp <= wfile.max_t:
                return wfile

    def getInfo(self, timestamp: float):
        wfile = self.__get(timestamp)
        return wfile.getInfo(timestamp)

    def Pressure(self, timestamp: float, dimension: str = 'mmrtst'):
        return self.__get(timestamp).Pressure(timestamp, dimension)

    def Temperature(self, timestamp: float):
        return self.__get(timestamp).Temperature(timestamp)

    def Rho_rel(self, timestamp: float):
        return self.__get(timestamp).Rho_rel(timestamp)

    def Rho_abs(self, timestamp: float):
        return self.__get(timestamp).Rho_abs(timestamp)

    def WindV(self, timestamp: float):
        return self.__get(timestamp).WindV(timestamp)

    def RainRt(self, timestamp: float):
        return self.__get(timestamp).RainRt(timestamp)