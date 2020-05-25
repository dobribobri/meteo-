# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

import os
import sys
import re
import numpy as np
from collections import defaultdict
from termcolor import colored
from settings import Settings
from borland.datetime import TDateTime


class WFile:
    def __init__(self, YYYY, MM, DD):
        self.YYYY = str(YYYY)
        self.MM = '{0:0>2}'.format(MM)
        self.DD = '{0:0>2}'.format(DD)
        self.wdatapath = os.path.join(Settings.meteoBaseDir,
                                      self.YYYY, self.MM, self.DD, 'data')
        self.WDATA = defaultdict(list)
        self.swp_tbl_parsed = False
        self.swp_tbl = defaultdict(list)
        self.min_t = TDateTime(YYYY, MM, DD).toDouble()
        self.max_t = TDateTime(YYYY, MM, DD, hh=23, mm=59, ss=59, ms=999).toDouble()

    def parse(self):
        if not os.path.exists(self.wdatapath):
            print('Не удалось обнаружить файл с данными погоды\t'
                  + '[' + colored('Error', 'red') + ']')
            return
        k = 0
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
                self.WDATA[timestamp] = [P, T, rho_rel, Wind, Rain_rt]
        self.sort_time()
        self.getTimeBounds()
        print('{}.{}.{} - Загрузка данных погоды. Ошибок: '.format(self.YYYY, self.MM, self.DD)
              + colored('{}\t'.format(k), 'red')
              + '[' + colored('OK', 'green') + ']')
        return

    @staticmethod
    def load_swprop():
        swvprc = defaultdict(list)
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
                swvprc[T_s] = [rho_s, p_s_kPa, p_s_mmrtst]
        print('Параметры насыщенного водяного пара\t'
              + '[' + colored('OK', 'green') + ']')
        return swvprc

    def set_swp_tbl(self, saturated_water_vapour_properties_table):
        self.swp_tbl = saturated_water_vapour_properties_table
        self.swp_tbl_parsed = True

    def sort_time(self):
        WDATA = defaultdict(list)
        for timestamp in sorted(self.WDATA.keys()):
            WDATA[timestamp] = self.WDATA[timestamp]
        self.WDATA = WDATA
        return

    def getTimeBounds(self):
        key_list = sorted(self.WDATA.keys())
        self.min_t, self.max_t = key_list[0], key_list[len(key_list) - 1]
        return self.min_t, self.max_t

    def cutWDATA(self, start_t: float, stop_t: float):
        self.WDATA = self.getCuttedWDATA(start_t, stop_t)

    def getCuttedWDATA(self, start_t: float, stop_t: float):
        newDATA = defaultdict(list)
        for timestamp in self.WDATA.keys():
            if start_t <= timestamp <= stop_t:
                newDATA[timestamp] = self.WDATA[timestamp]
        return newDATA

    def find_timestamp_closest_to(self, timestamp: float):
        if timestamp in self.WDATA.keys():
            return timestamp
        min_delta = sys.maxsize
        t = 0
        for key in self.WDATA.keys():
            if np.fabs(key - timestamp) < min_delta:
                min_delta = np.fabs(key - timestamp)
                t = key
        return t

    def getInfo(self, timestamp: float):
        key = self.find_timestamp_closest_to(timestamp)
        return self.WDATA[key][:]

    def Pressure(self, timestamp: float, dimension: str = 'mmrtst'):
        key = self.find_timestamp_closest_to(timestamp)
        if dimension == 'hpa':
            return self.WDATA[key][0] * 1.3332222
        return self.WDATA[key][0]

    def Temperature(self, timestamp: float):
        key = self.find_timestamp_closest_to(timestamp)
        return self.WDATA[key][1]

    def Rho_rel(self, timestamp: float):
        key = self.find_timestamp_closest_to(timestamp)
        return self.WDATA[key][2]

    def WindV(self, timestamp: float):
        key = self.find_timestamp_closest_to(timestamp)
        return self.WDATA[key][3]

    def RainRt(self, timestamp: float):
        key = self.find_timestamp_closest_to(timestamp)
        return self.WDATA[key][4]

    def Rho_abs(self, timestamp: float):
        if not self.swp_tbl_parsed:
            self.swp_tbl = WFile.load_swprop()
            self.swp_tbl_parsed = True
        T = float(np.round(self.Temperature(timestamp)))
        rho_s = self.swp_tbl[T][0]
        rho_abs = rho_s * self.Rho_rel(timestamp) / 100
        return rho_abs
