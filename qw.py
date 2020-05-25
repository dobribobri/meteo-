# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from measurement import Measurement
from weather import Weather
from rec_itu_p676_3 import Model
import default
import numpy as np
from collections import defaultdict
import time
import thinner
# from termcolor import colored
# import math
import sys
import itertools
import math
import scipy.integrate as Integrate


class QW:
    def __init__(self, m: Measurement, w: Weather, Tavg: float = 5, Tcl: float = -2,
                 theta: float = default.parameter.work.theta):
        self.Tavg = Tavg + 273
        self.tcl = Tcl
        self.theta = theta
        self.m = m
        self.w = w
        self.DATA = defaultdict(list)

    def get_integrals_multifreq(self, time_step_sec: int = 0):
        model = Model(theta=0.)
        for freq in self.m.DATA.keys():
            self.DATA[freq] = thinner.thin_out(self.m.DATA[freq], time_step_sec)
        # 21 - 24.4 // 25.4 - 27.2
        freq1 = np.arange(21.0, 24.5, 0.2)
        freq2 = np.arange(25.4, 27.3, 0.2)
        all_c = np.concatenate((freq1, freq2))
        # comb = [(f1, f2) for f1, f2 in itertools.combinations(all_c, 2)
        #         if not ((f1 in freq1 and f2 in freq1) or (f1 in freq2 and f2 in freq2))]
        l = sys.maxsize
        for key in all_c:
            l_ = len(self.DATA[np.round(key, decimals=1)])
            if l_ < l:
                l = l_
        if not l:
            exit(-11)
        Q, W = defaultdict(list), defaultdict(list)
        MIN = defaultdict(list)
        q_prev = 0
        for i in range(l):
            print(i)
            tau_exp, tauO, kw, krho, t = 0, 0, 0, 0, 0
            rho_avg = 0
            for f in all_c:
                f = np.round(f, decimals=1)

                timestamp, tb = self.DATA[f][i]
                t += timestamp
                T = self.w.Temperature(timestamp=timestamp)
                P = self.w.Pressure(timestamp=timestamp, dimension='hpa')
                rho = self.w.Rho_abs(timestamp=timestamp)
                rho_avg += rho
                model.setParameters(temperature=T, pressure=P, rho=rho)

                tau_exp += model.tau_experiment_zenith(T_br_theta=tb, T_avg=self.Tavg, theta=self.theta)
                tauO += model.tauO_theory(frequency=f)
                kw += model.kw(frequency=f, T_obl=self.tcl)
                krho += model.krho(frequency=f)
            t /= len(all_c)
            # abs(tau_exp - tauO - krho*Q - kw*W) -> min
            rho_avg /= len(all_c)
            if i == 0:
                q_init = Integrate.quad(lambda h: rho_avg * math.exp(- h / (model.H2 * 1000)),
                                        0, 100000)[0] / 10000
                q_start = q_init - 1
                q_stop = q_init + 1
            else:
                q_start = q_prev - q_prev / 100 * 30
                q_stop = q_prev + q_prev / 100 * 30

            q_, w_ = q_prev, 0
            min_ = sys.maxsize

            for q in np.arange(q_start, q_stop, 0.01):
                if q < 0:
                    continue
                for w in np.arange(0, 6, 0.01):
                    val = abs(tau_exp - tauO - krho*q - kw*w)
                    if val < min_:
                        min_ = val
                        q_, w_ = q, w
            q_prev = q_

            W['multifreq'].append((t, w_))
            Q['multifreq'].append((t, q_))
            MIN['multifreq'].append((t, min_))
        return Q, W, MIN

    def get_integrals(self, freq1: float, freq2: float, time_step_sec: int = 0, _w_shift: float = 0):
        for freq in self.m.DATA.keys():
            self.DATA[freq] = thinner.thin_out(self.m.DATA[freq], time_step_sec)
        Q, W = [], []
        model = Model(theta=0.)
        l1 = len(self.DATA[freq1])
        l2 = len(self.DATA[freq2])
        if l1 < l2:
            l_ = l1
        else:
            l_ = l2
        for i in range(l_):
            timestamp1, tb1 = self.DATA[freq1][i]
            timestamp2, tb2 = self.DATA[freq2][i]
            timestamp = (timestamp1 + timestamp2) / 2
            T = self.w.Temperature(timestamp=timestamp)
            P = self.w.Pressure(timestamp=timestamp, dimension='hpa')
            rho = self.w.Rho_abs(timestamp=timestamp)
            model.setParameters(temperature=T, pressure=P, rho=rho)

            M = np.array([[model.krho(frequency=freq1), model.kw(frequency=freq1, T_obl=self.tcl)],
                          [model.krho(frequency=freq2), model.kw(frequency=freq2, T_obl=self.tcl)]])

            v = np.array([model.tau_experiment_zenith(T_br_theta=tb1, T_avg=self.Tavg,
                                                      theta=self.theta)
                          - model.tauO_theory(frequency=freq1)
                                - model.kw(frequency=freq1, T_obl=self.tcl) * _w_shift,    #

                          model.tau_experiment_zenith(T_br_theta=tb2, T_avg=self.Tavg,
                                                      theta=self.theta)
                          - model.tauO_theory(freq2)
                                - model.kw(frequency=freq2, T_obl=self.tcl) * _w_shift    #
                          ])

            s = np.linalg.solve(M, v)
            Q.append((timestamp, s.tolist()[0]))
            W.append((timestamp, s.tolist()[1]))
        return Q, W

    def getQWDATA(self, freq_pairs: list, time_step_sec: int = 0, _w_correction=False):
        print("Расчёт параметров влагосодержания...\t")
        start_time = time.time()
        QDATA = defaultdict(list)
        WDATA = defaultdict(list)
        for freq1, freq2 in freq_pairs:
            print("Пара частот: {}, {} ГГц".format(freq1, freq2))
            Q, W = self.get_integrals(freq1, freq2, time_step_sec)
            for timestamp, val in Q:
                QDATA[(freq1, freq2)].append((timestamp, val))
            for timestamp, val in W:
                WDATA[(freq1, freq2)].append((timestamp, val))
        print('Времени затрачено: {:.3f} sec\t'.format(time.time() - start_time))
        # print('[' + colored('OK', 'green') + ']')
        if _w_correction:
            print('Корректировка значений...')
            return self.__w_correction_2(QDATA, WDATA, time_step_sec)
        return QDATA, WDATA

    # def __w_correction_1(self, WDATA):
    #     model = Model(theta=0.)
    #     NQDATA, NWDATA = defaultdict(list), defaultdict(list)
    #     for freq_pair in WDATA.keys():
    #         freq1, freq2 = freq_pair
    #         print("{}, {} ГГц".format(freq1, freq2))
    #         w_correction = sys.maxsize
    #         for _, w in WDATA[freq_pair]:
    #             if w < w_correction:
    #                 w_correction = w
    #         l1 = len(self.DATA[freq1])
    #         l2 = len(self.DATA[freq2])
    #         if l1 < l2:
    #             l_ = l1
    #         else:
    #             l_ = l2
    #         for i in range(l_):
    #             _, tb1 = self.DATA[freq1][i]
    #             _, tb2 = self.DATA[freq2][i]
    #             timestamp, W = WDATA[freq_pair][i]
    #             W_corrected = W - w_correction
    #             NWDATA[freq_pair].append((timestamp, W_corrected))
    #             Q_corrected = (model.tau_experiment_zenith(T_br_theta=tb1, T_avg=self.Tavg, theta=self.theta) +
    #                            model.tau_experiment_zenith(T_br_theta=tb2, T_avg=self.Tavg, theta=self.theta) -
    #                            model.tauO_theory(frequency=freq1) - model.tauO_theory(frequency=freq2) -
    #                            (model.kw(frequency=freq1, T_obl=self.tcl) + model.kw(frequency=freq2, T_obl=self.tcl)) *
    #                            W_corrected) / (model.krho(frequency=freq1) + model.krho(frequency=freq2))
    #             NQDATA[freq_pair].append((timestamp, Q_corrected))
    #     return NQDATA, NWDATA

    def __w_correction_2(self, QDATA, WDATA, time_step_sec: int):
        QDATA.clear()
        w_correction_dict = defaultdict(float)
        for freq1, freq2 in WDATA.keys():
            w_correction_value = sys.maxsize
            for _, w in WDATA[(freq1, freq2)]:
                if w < w_correction_value:
                    w_correction_value = w
            w_correction_dict[(freq1, freq2)] = w_correction_value
        WDATA.clear()
        print('Перерасчёт параметров...')
        start_time = time.time()
        NQDATA = defaultdict(list)
        NWDATA = defaultdict(list)
        for freq1, freq2 in w_correction_dict.keys():
            print("{}, {} ГГц".format(freq1, freq2))
            Q, W = self.get_integrals(freq1, freq2, time_step_sec, _w_shift=w_correction_dict[(freq1, freq2)])
            for timestamp, val in Q:
                NQDATA[(freq1, freq2)].append((timestamp, val))
            for timestamp, val in W:
                NWDATA[(freq1, freq2)].append((timestamp, val))
        print('Времени затрачено: {:.3f} sec\t'.format(time.time() - start_time))
        return NQDATA, NWDATA



