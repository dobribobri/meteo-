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
from termcolor import colored
from borland.datetime import TDateTime
import default
import time
from interquartile import Eliminate
from common import *


class TFile:
    def __init__(self, path: str, mode: str = ''):
        self.mode = mode
        if not mode:
            self.mode = 'standard'
        self.path = path
        self.session = Session()

    @staticmethod
    def __parse_line(text: str):
        return [elem for elem in re.split("[\t ]", re.sub("[\r\n]", '', text)) if elem]

    def parse(self, shift=True, rm_zeros=True, sort_freqs=True, sort_time=False,
              outliers_elimination=False, upper_threshold_val: float = None):
        print("Loading data from txt...\t", end='', flush=True)
        start_time = time.time()
        print('Current parser mode: ' + self.mode)
        with Switch(self.mode) as case:
            if case("standard"):
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
                        self.session.add(float(l_data[5])/1000, Point(timestamp, float(l_data[6])))
                        self.session.add(float(l_data[7])/1000, Point(timestamp, float(l_data[8])))
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
                        self.session.add(float(l_data[5]) / 1000, Point(timestamp, float(l_data[6])))
                        self.session.add(float(l_data[7]) / 1000, Point(timestamp, float(l_data[8])))
                    except ValueError:
                        continue
                t_file.close()

            if case("p"):
                # по процессорному времени
                t_file = open(self.path, "r")
                t_file.readline()
                for line in t_file:
                    l_data = TFile.__parse_line(line)
                    timestamp = float(l_data[3])
                    self.session.add(float(l_data[5]) / 1000, Point(timestamp, float(l_data[6])))
                    self.session.add(float(l_data[7]) / 1000, Point(timestamp, float(l_data[8])))
                t_file.close()

            if case("g1"):
                # режим гетеродин|1|x|
                t_file = open(self.path, "r")
                t_file.readline()
                for line in t_file:
                    l_data = TFile.__parse_line(line)
                    YYYY, MM, DD = l_data[0].split('.')
                    hh, mm, ss = l_data[1].split(':')
                    ms = l_data[2]
                    timestamp = TDateTime(YYYY, MM, DD, hh, mm, ss, ms).toDouble()
                    self.session.add(float(l_data[4])/1000, Point(timestamp, float(l_data[6])))
                t_file.close()

            if case("g2"):
                # режим гетеродин|x|1|
                t_file = open(self.path, "r")
                t_file.readline()
                for line in t_file:
                    l_data = TFile.__parse_line(line)
                    YYYY, MM, DD = l_data[0].split('.')
                    hh, mm, ss = l_data[1].split(':')
                    ms = l_data[2]
                    timestamp = TDateTime(YYYY, MM, DD, hh, mm, ss, ms).toDouble()
                    self.session.add(float(l_data[4]) / 1000, Point(timestamp, float(l_data[8])))
                t_file.close()

        print('{:.3f} sec\t'.format(time.time() - start_time), end='')
        print('[' + colored('OK', 'green') + ']')

        if shift:
            print('Overlay elimination...\t')
            self.shift()

        if rm_zeros:
            print('Removing zeros...\t')
            self.remove_zeros()

        if sort_freqs:
            print('Frequency sorting...\t')
            self.sort_frequencies()

        if sort_time:
            print('Time sorting...\t')
            self.sort_time()

        if outliers_elimination:
            print('Outliers elimination...\t')
            self.outliers_elimination()

        if upper_threshold_val:
            print('Setting threshold...\t')
            self.set_upp_threshold(upper_threshold_val)

    def shift(self):
        s_arr = default.parameter.freqs.shifted
        ssize = self.session.get_series(default.parameter.freqs.all[0]).length
        msize = self.session.get_series(s_arr[0]).length
        for f in s_arr:
            s = self.session.get_series(f)
            if s.is_empty:
                continue
            if s.length > 1.25 * ssize:
                k = 0
                data = []
                for i in range(0, s.length - 1, 2):
                    p = s.data[i]
                    p.merge(s.data[i+1])
                    data.append(p)
                    k += 1
                self.session.replace(s.freq, data)
                if k < msize:
                    msize = k

    def remove_zeros(self):
        self.session.remove_zeros(timeQ=True, valQ=True)

    def sort_frequencies(self):
        self.session.sort()

    def remove_time_zeros(self):
        self.session.remove_zeros(timeQ=True, valQ=False)

    def remove_val_zeros(self):
        self.session.remove_zeros(timeQ=False, valQ=True)

    def sort_time(self):
        self.session.time_sorting()

    def getDATA(self):
        return self.session.to_defaultdict()

    @property
    def DATA(self):
        return self.getDATA()

    def getTimeBounds(self):
        return self.session.get_time_bounds()

    def outliers_elimination(self):
        self.session.apply_to_series(Eliminate.time_series)

    def set_upp_threshold(self, threshold: float):
        self.session.set_upper_threshold(threshold)

    def cutDATA(self, start_t: float, stop_t: float):
        self.session.cut(start_t, stop_t)
