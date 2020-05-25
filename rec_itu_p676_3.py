# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from __future__ import division
from __future__ import print_function
import math
import scipy.integrate as Integrate
import numpy as np


class Model:
    # frequency - частота [ГГц]
    # Temperature - термодинамическая температура [град. Цельс.]
    # Pressure - атмосферное давление [гПа]
    # Rho - абсолютная влажность [г/м^3]
    # gammaO(freq) - погонный коэфф. поглощения в кислороде [Дб/км]
    # gammaRho(freq) - погонный коэфф. поглощения водяного пара [Дб/км]
    # tau_theory(freq) - полное поглощение в атмосфере (теор.) [нп] (theta - зенитный угол [радианы])
    # tau_experiment(T_br, T_avg) - полное поглощение по известной яркостной T_br [K] температуре
    #                                   и средней температуре T_avg = T0 - dT [K] (зенит).
    # get_Q() - полная масса водяного пара как интеграл от rho0*exp(-H/H_характ.)
    # tau_полное = tau_кислорода + k_rho * Q + k_w * W

    def __init__(self, Temperature: float = 15.,
                 Pressure: float = 1013., Rho: float = 7.5, theta: float = 0.):
        self.T = Temperature
        self.P = Pressure
        self.rho = Rho
        self.theta = theta
        self.H1 = 5
        self.H2 = 2.1  # 1.8
        self.c = 299792458
        self.dB2np = 0.23255814

    # Погонный коэфф. поглощения в кислороде
    def gammaO(self, frequency: float):
        rp = self.P / 1013
        rt = 288 / (273 + self.T)
        f = frequency
        gamma = 0
        if f <= 57:
            gamma = (7.27 * rt / (f * f + 0.351 * rp * rp * rt * rt) +
                     7.5 / ((f - 57) ** 2 + 2.44 * rp * rp * rt ** 5)) * \
                    f * f * rp * rp * rt * rt / 1000
        elif 63 <= f <= 350:
            gamma = (2 / 10000 * pow(rt, 1.5) * (1 - 1.2 / 100000 * pow(f, 1.5)) +
                     4 / ((f - 63) ** 2 + 1.5 * rp * rp * rt ** 5) +
                     0.28 * rt * rt / ((f - 118.75) ** 2 + 2.84 * rp * rp * rt * rt)) * \
                    f * f * rp * rp * rt * rt / 1000
        elif 57 < f < 63:
            gamma = (f - 60) * (f - 63) / 18 * self.gammaO(57) - \
                    1.66 * rp * rp * pow(rt, 8.5) * (f - 57) * (f - 63) + \
                    (f - 57) * (f - 60) / 18 * self.gammaO(63)
        return gamma        # в Дб/км

    # Погонный коэфф. поглощения в водяном паре
    def gammaRho(self, frequency: float):
        rp = self.P / 1013
        rt = 288 / (273 + self.T)
        f = frequency
        rho = self.rho
        gamma = 0
        if f <= 350:
            gamma = (3.27 / 100 * rt +
                     1.67 / 1000 * rho * rt ** 7 / rp +
                     7.7 / 10000 * pow(f, 0.5) +
                     3.79 / ((f - 22.235) ** 2 + 9.81 * rp * rp * rt) +
                     11.73 * rt / ((f - 183.31) ** 2 + 11.85 * rp * rp * rt) +
                     4.01 * rt / ((f - 325.153) ** 2 + 10.44 * rp * rp * rt)) * \
                    f * f * rho * rp * rt / 10000
        return gamma        # в Дб/км

    # Полное поглощение в кислороде (модельн.). Учитывает угол наблюдения.
    def tauO_theory(self, frequency: float):
        return self.gammaO(frequency) * self.H1 / math.cos(self.theta) * self.dB2np      # в неперах

    # Полное поглощение в водяном паре (модельн.). Учитывает угол наблюдения.
    def tauRho_theory(self, frequency: float):
        return self.gammaRho(frequency) * self.H2 / math.cos(self.theta) * self.dB2np    # в неперах

    # Полное поглощение (оптическая толщина tau*) - модельное. Учитывает угол наблюдения.
    def tau_theory(self, frequency: float):
        return self.tauO_theory(frequency) + self.tauRho_theory(frequency)                # в неперах

    # ---- Для проверки модели ----
    # # Яркостная температура (модельн.). Учитывает угол наблюдения.
    # def get_Tb_model(self, freq, T_avg, viaQ=False):
    #     if viaQ:
    #         Q = self.__Q()
    #         tau = self.tauO_theory(freq) + self.krho(freq) * Q  # Здесь tau = tau* / cos(theta)
    #         T_br = (T_avg + 273) * (1 - math.exp(-tau))
    #         return T_br
    #     return (T_avg + 273) * (1 - math.exp(-self.tau_theory(freq)))

    # Полное поглощение в зените по (экспериментально) измеренной яркостной температуре на углу theta
    @staticmethod
    def tau_experiment_zenith(T_br_theta: float, theta: float, T_avg: float):   # Температуры в Кельвинах
        tau = -math.log((T_br_theta - T_avg) / ((-1) * T_avg)) * math.cos(theta)
        return tau        # в неперах

    # @staticmethod
    # def tau_experiment(T_br: float, T_avg: float):   # Температуры в Кельвинах
    #     tau = -math.log((T_br - T_avg) / ((-1) * T_avg))
    #     return tau

    # Полная масса водяного пара в столбе атмосферы как интеграл от rho0*exp(-H/H_характ.)
    def __Q(self):
        func = lambda h: self.rho * math.exp(- h / (self.H2 * 1000))
        Q = Integrate.quad(func, 0, 100000)
        return Q[0] / 10000

    # Весовая функция 1. Учитывает угол наблюдения.
    def krho(self, frequency: float):
        return self.tauRho_theory(frequency) / self.__Q()
        # return self.tauRho_theory(frequency) / 1.575

    # Диэлектрическая проницаемость воды при данной температуре, солёности и длине волны.
    @staticmethod
    def __epsilon(temperature: float, saltiness: float, lamda: float):
        T = temperature
        Sw = saltiness
        epsO_nosalt = 5.5
        epsS_nosalt = 88.2 - 0.40885 * T + 0.00081 * T * T
        lamdaS_nosalt = 1.8735116 - 0.027296 * T + 0.000136 * T * T + 1.662 * math.exp(-0.0634 * T)
        EpsO = epsO_nosalt
        EpsS = epsS_nosalt - 17.2 * Sw / 60
        lamdaS = lamdaS_nosalt - 0.206 * Sw / 60
        Eps1 = EpsO + (EpsS - EpsO) / (1 + (lamdaS / lamda) ** 2)
        Eps2 = lamdaS / lamda * (EpsS - EpsO) / (1 + (lamdaS / lamda) ** 2)
        EPS = []
        EPS.append(Eps1)  # EPS[0]
        EPS.append(Eps2)  # EPS[1]
        EPS.append(EpsO)  # EPS[2]
        EPS.append(EpsS)  # EPS[3]
        EPS.append(lamdaS)  # EPS[4]
        return EPS

    def epsilon(self, temperature: float, saltiness: float, frequency: float):
        lamda = self.c / (frequency * 10 ** 9) * 100  # перевод в [cm]
        eps_1, eps_2, _, _, _ = self.__epsilon(temperature, saltiness, lamda)
        return complex(eps_1, eps_2)

    # Весовая функция 2. Не учитывает угол наблюдения. Учитывает температуру облака.
    def kw(self, frequency: float, T_obl: float = -2):
        lamda = self.c / (frequency * 10 ** 9) * 100  # перевод в [cm]
        _, _, EpsO, EpsS, lamdaS = self.__epsilon(T_obl, 0, lamda)
        y = lamdaS / lamda
        # kw = 8.18 / lamda * (-3) * (EpsO - EpsS) * y / ((EpsS+2)**2 + (EpsO+2)**2 * y*y) / 10.
        kw = 0.6 * math.pi / lamda * (-3) * (EpsO - EpsS) * y / ((EpsS + 2) ** 2 + (EpsO + 2) ** 2 * y * y)
        return kw

    # ---- Для проверки модели ----
    # def ImEpsCm1p2(self, frequency, T_obl = -2):
    #     lamda = self.c / (frequency * 10**9) * 100    # перевод в [cm]
    #     Sw = 0
    #     EPS = self.__epsilon(T_obl, Sw, lamda)
    #     EpsO = EPS[2]
    #     EpsS = EPS[3]
    #     lamdaS = EPS[4]
    #     y = lamdaS / lamda
    #     k = - (-3) * (EpsO - EpsS) * y / ((EpsS+2)**2 + (EpsO+2)**2 * y*y) * 1000.
    #     return k

    # ---- Для проверки модели ----
    # def Y(self, frequency, T_obl = -2):
    #     lamda = self.c / (frequency * 10**9) * 100    # перевод в [cm]
    #     Sw = 0
    #     EPS = self.__epsilon(T_obl, Sw, lamda)
    #     lamdaS = EPS[4]
    #     y = lamdaS / lamda
    #     return y

    # ---- Для проверки модели ----
    # def _get_QW_model_zenith(self, freq1, freq2, T_obl = -2):
    #     mem_theta = self.theta
    #     self.theta = 0
    #
    #     M = np.array([[self.krho(freq1), self.kw(freq1, T_obl)],
    #                   [self.krho(freq2), self.kw(freq2, T_obl)]])
    #     v = np.array([self.tau_theory(freq1) - self.tauO_theory(freq1),
    #                   self.tau_theory(freq2) - self.tauO_theory(freq2)])
    #     s = np.linalg.solve(M, v)
    #
    #     self.theta = mem_theta
    #     return s.tolist()[0], s.tolist()[1]

    def setRho(self, rho: float):
        self.rho = rho
        return

    def setTheta(self, theta: float):
        self.theta = theta
        return

    def setTemperature(self, T: float):
        self.T = T
        return

    def setPressure(self, P: float):
        self.P = P
        return

    def setParameters(self, temperature: float = None,
                      pressure: float = None, rho: float = None, theta: float = None):
        if temperature:
            self.T = temperature
        if pressure:
            self.P = pressure
        if rho:
            self.rho = rho
        if theta:
            self.theta = theta
        return
