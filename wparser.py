# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from session import *
import os
import re
from termcolor import colored
from settings import Settings
from settings import parameter as p
from borland_datetime import *


class WFile:
    def __init__(self, YYYY: Union[int, str], MM: Union[int, str], DD: Union[int, str]):
        self.YYYY = str(YYYY)
        self.MM = '{0:0>2}'.format(MM)
        self.DD = '{0:0>2}'.format(DD)
        self.wdatapath = os.path.join(Settings.meteoBaseDir,
                                      self.YYYY, self.MM, self.DD, 'data')
        self.WDATA = Session()
        self.swvp_tbl = WFile.load_swv_prop()
        self.min_t = TDateTime(YYYY, MM, DD).toDouble()
        self.max_t = TDateTime(YYYY, MM, DD, **END_OF_DAY).toDouble()

    @staticmethod
    def fromDate(Date: date) -> 'WFile':
        return WFile(Date.year, Date.month, Date.day)

    def parse(self) -> None:
        if not os.path.exists(self.wdatapath):
            print('No weather files found\t'
                  + '[' + colored('Error', 'red') + ']')
            return
        k = 0
        self.WDATA.series.clear()
        with open(self.wdatapath, 'r') as wdatafile:
            for line in wdatafile:
                l_data = re.split("[\t ]", re.sub("[\r\n]", '', line))
                l_data = [elem for elem in l_data if elem]
                try:
                    time = l_data[0]
                    t_data = re.split(':', time)
                    hh, mm = int(t_data[0]), int(t_data[1])
                    P = float(l_data[1])
                    T = float(l_data[2])
                    rho_rel = float(l_data[3])
                    Wind = float(l_data[4])
                    Rain_rt = float(l_data[5])
                except IndexError or ValueError:
                    k += 1
                    continue
                timestamp = TDateTime(self.YYYY, self.MM, self.DD, hh, mm).toDouble()
                self.WDATA.add(p.weather.labels.T_C, Point(timestamp, T))
                self.WDATA.add(p.weather.labels.T_K, Point(timestamp, T - 273.15))
                self.WDATA.add(p.weather.labels.P_mm, Point(timestamp, P))
                self.WDATA.add(p.weather.labels.P_hpa, Point(timestamp, P * 1.3332222))
                self.WDATA.add(p.weather.labels.rho_rel, Point(timestamp, rho_rel))
                rho_s = self.swvp_tbl[int(T)][0]
                rho_abs = rho_s * rho_rel / 100
                self.WDATA.add(p.weather.labels.rho_abs, Point(timestamp, rho_abs))
                self.WDATA.add(p.weather.labels.Vwind, Point(timestamp, Wind))
                self.WDATA.add(p.weather.labels.RainRt, Point(timestamp, Rain_rt))

        self.min_t, self.max_t = self.WDATA.get_time_bounds()
        # print('{}.{}.{} - Загрузка данных погоды. Ошибок: '.format(self.YYYY, self.MM, self.DD)
        #       + colored('{}\t'.format(k), 'red')
        #       + '[' + colored('OK', 'green') + ']')
        return

    @staticmethod
    def load_swv_prop() -> defaultdict:
        data = defaultdict(list)
        k = 0
        with open(Settings.swvapour_conf_path, 'r') as swvcfile:
            for line in swvcfile:
                l_data = re.split("[\t ]", re.sub("[\r\n]", '', line))
                l_data = [elem for elem in l_data if elem]
                try:
                    T_s = float(l_data[0])
                    p_s_mmrtst = float(l_data[1])
                    p_s_kPa = float(l_data[2])
                    rho_s = float(l_data[3])
                except IndexError or ValueError:
                    k += 1
                    continue
                data[T_s] = [rho_s, p_s_kPa, p_s_mmrtst]
        # print('Параметры насыщенного водяного пара\t'
        #       + '[' + colored('OK', 'green') + ']')
        return data

    def cutData(self, start_t: float, stop_t: float) -> None:
        self.WDATA.cut(start_t, stop_t)

    def getInfo(self, timestamp: float) -> list:
        return self.WDATA.get_spectrum(timestamp)

    def Pressure(self, timestamp: float, dimension: str = p.weather.labels.P_mm) -> float:
        return self.WDATA.get_series(key=dimension).get(timestamp)

    def Temperature(self, timestamp: float, dimension: str = p.weather.labels.T_C) -> float:
        return self.WDATA.get_series(key=dimension).get(timestamp)

    def Rho_rel(self, timestamp: float) -> float:
        return self.WDATA.get_series(key=p.weather.labels.rho_rel).get(timestamp)

    def Rho_abs(self, timestamp: float) -> float:
        return self.WDATA.get_series(key=p.weather.labels.rho_abs).get(timestamp)

    def WindV(self, timestamp: float) -> float:
        return self.WDATA.get_series(key=p.weather.labels.Vwind).get(timestamp)

    def RainRt(self, timestamp: float) -> float:
        return self.WDATA.get_series(key=p.weather.labels.RainRt).get(timestamp)
