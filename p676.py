# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from typing import Tuple
import math
import scipy.integrate as Integrate


class Model:
    def __init__(self, Temperature: float = 15., Pressure: float = 1013., Rho: float = 7.5,
                 theta: float = 0., rainQ=False):
        """
        :param Temperature: термодинамическая температура [град. Цельс.]
        :param Pressure: атмосферное давление [гПа]
        :param Rho: абсолютная влажность [г/м^3]
        :param theta: угол наблюдения [рад.]
        """
        self.T = Temperature
        self.P = Pressure
        self.rho = Rho
        self.theta = theta
        self.rainQ = rainQ
        self.c = 299792458
        self.dB2np = 0.23255814

    @staticmethod
    def H1(frequency: float) -> float:
        """
        :return: характеристическая высота поглощения в кислороде (км)
        """
        f = frequency
        if f < 50:
            return 6
        elif 70 < f < 350:
            return 6 + 40 / ((f - 118.7) ** 2 + 1)
        return 6

    @staticmethod
    def H2(frequency: float, rainQ: bool) -> float:
        """
        :param frequency: частота излучения
        :param rainQ: дождь?
        :return: характеристическая высота поглощения в водяном паре (км)
        """
        f = frequency
        Hw = 1.6
        if rainQ:
            Hw = 2.1
        return Hw * (1 + 3. / ((f - 22.2) ** 2 + 5) + 5. / ((f - 183.3) ** 2 + 6) +
                     2.5 / ((f - 325.4) ** 2 + 4))

    def gammaO(self, frequency: float) -> float:
        """
        :return: погонный коэффициент поглощения в кислороде (Дб/км)
        """
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
        return gamma

    def gammaRho(self, frequency: float) -> float:
        """
        :return: погонный коэффициент поглощения в водяном паре (Дб/км)
        """
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
        return gamma

    def tauO_theory(self, frequency: float) -> float:
        """
        Учитывает угол наблюдения.

        :return: полное поглощение в кислороде (модельн.). В неперах
        """
        return self.gammaO(frequency) * Model.H1(frequency) / math.cos(self.theta) * self.dB2np

    def tauRho_theory(self, frequency: float) -> float:
        """
        Учитывает угол наблюдения.

        :return: полное поглощение в водяном паре (модельн.). В неперах
        """
        return self.gammaRho(frequency) * Model.H2(frequency, self.rainQ) / math.cos(self.theta) * self.dB2np

    def tau_theory(self, frequency: float) -> float:
        """
        Учитывает угол наблюдения.

        :return: полное поглощение (оптическая толщина) - модельное. В неперах
        """
        return self.tauO_theory(frequency) + self.tauRho_theory(frequency)

    @staticmethod
    def opacity(brT: float, Tavg: float) -> float:
        """
        Оценка на полное поглощение в зените.

        :param brT: яркостная температура (К) в направлении зенита
        :param Tavg: средняя эффективная температура атмосферы (К)
        :return: неперы
        """
        return -math.log((brT - Tavg) / (-Tavg))

    @staticmethod
    def Q(rho0: float = 7.5, Hrho: float = 1.8) -> float:
        """
        :return: полная масса водяного пара в столбе атмосферы как интеграл от rho0*exp(-H/H_характ.) [г/см2]
        """
        func = lambda h: rho0 * math.exp(- h / (Hrho * 1000))
        # noinspection PyTypeChecker
        Q = Integrate.quad(func, 0, 100000)
        return Q[0] / 10000

    def krho(self, frequency: float) -> float:
        """
        Учитывает угол наблюдения. В неперах.

        :return: весовая функция k_rho (водяной пар).
        """
        # Q = Model.Q(rho0=self.rho, Hrho=Model.H2(frequency, self.rainQ))
        Q = Model.Q(rho0=self.rho, Hrho=1.6)
        # Q = Model.Q(rho0=10, Hrho=Model.H2(frequency, self.rainQ))
        # Q = Model.Q(rho0=10, Hrho=1.8)
        # Q = 1.575
        # print(frequency, Q)
        return self.tauRho_theory(frequency) / Q

    @staticmethod
    def epsilon(T: float, Sw: float) -> Tuple[float, float, float]:
        """
        Расчёт диэлектрической проницаемости.

        :param T: температура воды
        :param Sw: соленость воды
        :return:
        """
        epsO_nosalt = 5.5
        epsS_nosalt = 88.2 - 0.40885 * T + 0.00081 * T * T
        lambdaS_nosalt = 1.8735116 - 0.027296 * T + 0.000136 * T * T + 1.662 * math.exp(-0.0634 * T)
        epsO = epsO_nosalt
        epsS = epsS_nosalt - 17.2 * Sw / 60
        lambdaS = lambdaS_nosalt - 0.206 * Sw / 60
        return epsO, epsS, lambdaS

    def kw(self, frequency: float, tcl: float) -> float:
        """
        Не учитывает угол наблюдения. В неперах.

        :param frequency: частота излучения
        :param tcl: средняя эффективная температура облака
        :return: весовая функция k_w (вода в жидкокапельной фазе).
        """
        lamda = self.c / (frequency * 10 ** 9) * 100  # перевод в [cm]
        epsO, epsS, lambdaS = Model.epsilon(tcl, 0.)
        y = lambdaS / lamda
        return 3 * 0.6*math.pi / lamda * (epsS - epsO) * y / (
                (epsS + 2) ** 2 + (epsO + 2) ** 2 * y * y)

    def setParameters(self, temperature: float = None,
                      pressure: float = None, rho: float = None, theta: float = None) -> None:
        if temperature:
            self.T = temperature
        if pressure:
            self.P = pressure
        if rho:
            self.rho = rho
        if theta:
            self.theta = theta
