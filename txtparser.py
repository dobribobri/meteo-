# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from __future__ import division
from __future__ import print_function
import re
from switch import Switch
from collections import defaultdict
from termcolor import colored
from borland.datetime import TDateTime
import default
import time
import sys
import numpy as np
from interquartile import Eliminate


class TFile:
    def __init__(self, path: str, mode: str = ''):
        self.mode = mode
        self.path = path
        self.DATA = defaultdict(list)

    @staticmethod
    def __parse_line(text: str):
        l_data = re.split("[\t ]", re.sub("[\r\n]", '', text))
        l_data = [elem for elem in l_data if elem]
        return l_data

    # def __file_not_empty(self, filePath: str):
    #     return os.path.getsize(filePath) > 0

    def parse(self, shift=True, rm_zeros=True, sort_freqs=True, sort_time=False,
              outliers_elimination=False, upper_threshold_val: float = None):
        print("Загрузка данных в оперативную память...\t", end='', flush=True)
        start_time = time.time()
        print('Current parser mode: ' + self.mode)
        with Switch(self.mode) as case:
            if case(""):
                # стандартный режим
                t_file = open(self.path, "r", encoding='cp1251')
                t_file.readline()
                for line in t_file:
                    try:
                        l_data = TFile.__parse_line(line)
                        YYYY, MM, DD = l_data[0].split('.')
                        hh, mm, ss = l_data[1].split(':')
                        ms = l_data[2]
                        timestamp = TDateTime(YYYY, MM, DD, hh, mm, ss, ms).toDouble()
                        self.DATA[float(l_data[5])/1000].append((timestamp, float(l_data[6])))
                        self.DATA[float(l_data[7])/1000].append((timestamp, float(l_data[8])))
                    except ValueError:
                        continue
                t_file.close()
            if case("DDMMYY"):
                t_file = open(self.path, "r", encoding='cp1251')
                t_file.readline()
                for line in t_file:
                    try:
                        l_data = TFile.__parse_line(line)
                        DD, MM, YY = l_data[0].split('.')
                        YYYY = str(int(YY) + 2000)
                        hh, mm, ss = l_data[1].split(':')
                        ms = l_data[2]
                        timestamp = TDateTime(YYYY, MM, DD, hh, mm, ss, ms).toDouble()
                        self.DATA[float(l_data[5])/1000].append((timestamp, float(l_data[6])))
                        self.DATA[float(l_data[7])/1000].append((timestamp, float(l_data[8])))
                    except ValueError:
                        continue
                t_file.close()

            # if case("p"):
            #     # по процессорному времени
            #     t_file = open(self.path, "r")
            #     t_file.readline()
            #     for line in t_file:
            #         l_data = TFile.__parse_line(line)
            #         timestamp = float(l_data[3])
            #         self.DATA[float(l_data[5])/1000].append((timestamp, float(l_data[6])))
            #         self.DATA[float(l_data[7])/1000].append((timestamp, float(l_data[8])))
            #     t_file.close()

            # if case("g1"):
            #     # режим гетеродин|1|x|
            #     t_file = open(self.path, "r")
            #     t_file.readline()
            #     for line in t_file:
            #         l_data = TFile.__parse_line(line)
            #         YYYY, MM, DD = l_data[0].split('.')
            #         hh, mm, ss = l_data[1].split(':')
            #         ms = l_data[2]
            #         timestamp = TDateTime(YYYY, MM, DD, hh, mm, ss, ms).toDouble()
            #         self.DATA[float(l_data[4])/1000].append((timestamp, float(l_data[6])))
            #     t_file.close()

            # if case("g2"):
            #     # режим гетеродин|x|1|
            #     t_file = open(self.path, "r")
            #     t_file.readline()
            #     for line in t_file:
            #         l_data = TFile.__parse_line(line)
            #         YYYY, MM, DD = l_data[0].split('.')
            #         hh, mm, ss = l_data[1].split(':')
            #         ms = l_data[2]
            #         timestamp = TDateTime(YYYY, MM, DD, hh, mm, ss, ms).toDouble()
            #         self.DATA[float(l_data[4])/1000].append((timestamp, float(l_data[8])))
            #     t_file.close()

        print('{:.3f} sec\t'.format(time.time() - start_time), end='')
        print('[' + colored('OK', 'green') + ']')

        if shift:
            print('Устранение наложений...\t')
            self.shift()

        if rm_zeros:
            print('Удаление нулей...\t')
            self.remove_time_zeros()
            self.remove_val_zeros()

        if sort_freqs:
            print('Сортировка по частотам...\t')
            self.sort_frequencies()

        if sort_time:
            print('Сортировка по времени...\t')
            self.sort_time()

        if outliers_elimination:
            print('Устранение явных выбросов...\t')
            self.outliers_elimination(threshold_percentage=20)

        if upper_threshold_val:
            print('Устранение значений выше порогового...\t')
            self.upper_threshold_elimination(upper_threshold_val)
        return

    def shift(self):
        ssize = len(self.DATA[default.parameter.freqs.ALL[0]])
        msize = len(self.DATA[default.parameter.freqs.SHIFTED[0]])
        s_arr = default.parameter.freqs.SHIFTED
        for f in s_arr:
            if not self.DATA[f]:
                # print(f)
                continue
            l = len(self.DATA[f])
            if l > 1.25 * ssize:
                k = 0
                av = []
                for i in range(0, l-1, 2):
                    t_i, x_i = self.DATA[f][i]
                    t_i1, x_i1 = self.DATA[f][i+1]
                    t = (t_i + t_i1) / 2
                    x = (x_i + x_i1) / 2
                    av.append((t, x))
                    k += 1
                self.DATA[f] = av
                if k < msize: msize = k
        return

    def remove_zeros(self):
        data = defaultdict(list)
        for freq in self.DATA.keys():
            for time, val in self.DATA[freq]:
                if (time != 0) and (val != 0):
                    data[freq].append((time, val))
                else:
                    print(colored('Удаление единичного измерения. ' +
                                  'Частота: {}\t Время {} (TDateTime)\t Значение {}'.format(
                                      freq, time, val
                                  ), 'red'))
        self.DATA = data
        return

    def sort_frequencies(self):
        data = defaultdict(list)
        for freq in sorted(self.DATA.keys()):
            data[freq] = self.DATA[freq]
        self.DATA = data
        return

    def remove_time_zeros(self):
        data = defaultdict(list)
        errors = 0
        for freq in self.DATA.keys():
            for time, val in self.DATA[freq]:
                if time != 0:
                    data[freq].append((time, val))
                else:
                    errors += 1
        if errors:
            print(colored('Единичных измерений с нулевым значением времени: {}'.format(errors), 'red'))
        self.DATA = data
        return

    def remove_val_zeros(self):
        data = defaultdict(list)
        errors = 0
        for freq in self.DATA.keys():
            for time, val in self.DATA[freq]:
                if val != 0:
                    data[freq].append((time, val))
                else:
                    errors += 1
        if errors:
            print(colored('Единичных измерений с нулевым значением температуры: {}'.format(errors), 'red'))
        self.DATA = data
        return

    def sort_time(self):
        for freq in self.DATA.keys():
            self.DATA[freq] = sorted(self.DATA[freq], key=lambda t: t[0])
        return

    def getDATA(self):
        return self.DATA[:]

    def getTimeBounds(self):
        min_t, max_t = sys.maxsize, 0
        for key in self.DATA.keys():
            for t, _ in self.DATA[key]:
                if t < min_t:
                    min_t = t
                if t > max_t:
                    max_t = t
        return min_t, max_t

    def outliers_elimination(self, threshold_percentage: float = None):
        for freq in self.DATA.keys():
            self.DATA[freq] = Eliminate.time_series(self.DATA[freq], threshold_percentage)
        return

    def upper_threshold_elimination(self, threshold: float):
        DATA = defaultdict(list)
        for freq in self.DATA.keys():
            for t, v in self.DATA[freq]:
                if v < threshold:
                    DATA[freq].append((t, v))
        self.DATA = DATA
        return

    def cutDATA(self, start_t: float, stop_t: float):
        self.DATA = self.getCuttedDATA(start_t, stop_t)

    def getCuttedDATA(self, start_t: float, stop_t: float):
        newDATA = defaultdict(list)
        for key in self.DATA.keys():
            for t, v in self.DATA[key]:
                if start_t <= t <= stop_t:
                    newDATA[key].append((t, v))
        return newDATA

    def find_timestamp_closest_to(self, keyfreq: float, timestamp: float):
        min_delta = sys.maxsize
        t = 0
        for time_, _ in self.DATA[keyfreq]:
            if np.fabs(time_ - timestamp) < min_delta:
                min_delta = np.fabs(time_ - timestamp)
                t = time_
        return t
