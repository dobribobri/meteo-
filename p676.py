# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from typing import Tuple, Union
import math
import scipy.integrate as Integrate
import numpy as np


C = 299792458
dB2np = 0.23255814


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

        self.TK = 0.     # Температура космического фона

    @staticmethod
    def H1(frequency: float) -> float:
        """
        :return: характеристическая высота поглощения в кислороде (км)
        """
        f = frequency
        const = 6   # 6 rec.ITU-R  # 5.3 suggested
        if f < 50:
            return const
        elif 70 < f < 350:
            return const + 40 / ((f - 118.7) ** 2 + 1)
        return const

    @staticmethod
    def H2(frequency: float, rainQ: bool) -> float:
        """
        :param frequency: частота излучения
        :param rainQ: дождь?
        :return: характеристическая высота поглощения в водяном паре (км)
        """
        f = frequency
        Hw = 1.6   # 1.6 rec.ITU-R
        if rainQ:
            Hw = 2.1
        return Hw * (1 + 3. / ((f - 22.2) ** 2 + 5) + 5. / ((f - 183.3) ** 2 + 6) +
                     2.5 / ((f - 325.4) ** 2 + 4))

    def gammaO(self, frequency: float) -> float:
        """
        :return: погонный коэффициент поглощения в кислороде (Дб/км)
        """
        return Model.gammaOxygen(frequency, self.T, self.P)
    
    @staticmethod
    def gammaOxygen(frequency: float, T: Union[float, np.ndarray], P: Union[float, np.ndarray]):
        """
        :return: погонный коэффициент поглощения в кислороде (Дб/км)
        """
        rp = P / 1013
        rt = 288 / (273 + T)
        f = frequency
        gamma = 0
        if f <= 57:
            gamma = (7.27 * rt / (f * f + 0.351 * rp * rp * rt * rt) +
                     7.5 / ((f - 57) ** 2 + 2.44 * rp * rp * np.power(rt, 5))) * \
                    f * f * rp * rp * rt * rt / 1000
        elif 63 <= f <= 350:
            gamma = (2 / 10000 * np.power(rt, 1.5) * (1 - 1.2 / 100000 * pow(f, 1.5)) +
                     4 / ((f - 63) ** 2 + 1.5 * rp * rp * rt ** 5) +
                     0.28 * rt * rt / ((f - 118.75) ** 2 + 2.84 * rp * rp * rt * rt)) * \
                    f * f * rp * rp * rt * rt / 1000
        elif 57 < f < 63:
            gamma = (f - 60) * (f - 63) / 18 * Model.gammaOxygen(57, T, P) - \
                    1.66 * rp * rp * pow(rt, 8.5) * (f - 57) * (f - 63) + \
                    (f - 57) * (f - 60) / 18 * Model.gammaOxygen(63, T, P)
        return gamma

    def gammaRho(self, frequency: float) -> float:
        """
        :return: погонный коэффициент поглощения в водяном паре (Дб/км)
        """
        return Model.gammaWVapor(frequency, self.T, self.P, self.rho)
    
    @staticmethod
    def gammaWVapor(frequency: float,
                    T: Union[float, np.ndarray],
                    P: Union[float, np.ndarray],
                    rho: Union[float, np.ndarray]):
        """
        :return: погонный коэффициент поглощения в водяном паре (Дб/км)
        """
        rp = P / 1013
        rt = 288 / (273 + T)
        f = frequency
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

    @staticmethod
    def gammaWVaporBarettChung(frequency: float,
                    T: Union[float, np.ndarray],
                    P: Union[float, np.ndarray],
                    rho: Union[float, np.ndarray]):
        """
        :return: погонный коэффициент поглощения в водяном паре (Дб/км)
        """
        f = frequency
        T = T + 273.15
        df = 2.58 * 0.001 * (1 + rho * T / P) / np.power(T / 318, 0.625)
        gamma = 32.4 * np.exp(-644 / T) * f*f * P * rho / np.power(T, 3.125) * (1 + 0.0147 * rho * T / P) * \
            (1/((f - 22.235) * (f - 22.235) + df * df) + 1/((f + 22.235)*(f + 22.235) + df * df)) + \
            2.55 * 0.001 * rho * f*f * df / np.power(T, 3/2)
        return gamma

    def tauO_theory(self, frequency: float) -> float:
        """
        Учитывает угол наблюдения.

        :return: полное поглощение в кислороде (модельн.). В неперах
        """
        return self.gammaO(frequency) * Model.H1(frequency) / math.cos(self.theta) * dB2np

    def tauRho_theory(self, frequency: float) -> float:
        """
        Учитывает угол наблюдения.

        :return: полное поглощение в водяном паре (модельн.). В неперах
        """
        return self.gammaRho(frequency) * Model.H2(frequency, self.rainQ) / math.cos(self.theta) * dB2np

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
    def Q(rho0: float = 7.5, Hrho: float = 2.1) -> float:
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
        Q = Model.Q(rho0=self.rho, Hrho=2.1)
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

    @staticmethod
    def kw(frequency: float, tcl: float) -> float:
        """
        Не учитывает угол наблюдения. В неперах.

        :param frequency: частота излучения
        :param tcl: средняя эффективная температура облака
        :return: весовая функция k_w (вода в жидкокапельной фазе).
        """
        lamda = C / (frequency * 10 ** 9) * 100  # перевод в [cm]
        epsO, epsS, lambdaS = Model.epsilon(tcl, 0.)
        y = lambdaS / lamda
        return 3 * 0.6*math.pi / lamda * (epsS - epsO) * y / (
                (epsS + 2) ** 2 + (epsO + 2) ** 2 * y * y)
    
    @staticmethod
    def gammaLWater(frequency: float, tcl: float) -> float:
        """
        Не учитывает угол наблюдения. В децибелах.

        :param frequency: частота излучения
        :param tcl: средняя эффективная температура облака
        :return: весовая функция k_w (вода в жидкокапельной фазе).
        """
        return Model.convert_np2dB(Model.kw(frequency, tcl))

    def setParameters(self, temperature: float = None,
                      pressure: float = None,
                      rho: float = None,
                      theta: float = None) -> None:
        if temperature:
            self.T = temperature
        if pressure:
            self.P = pressure
        if rho:
            self.rho = rho
        if theta:
            self.theta = theta
    
    @staticmethod
    def convert_np2dB(val):
        return (1/dB2np) * val
    
    @staticmethod
    def convert_dB2np(val):
        return dB2np * val

    @staticmethod
    def epsilon_c(frequency: float, T: float, Sw: float):
        lamda = C / (frequency * 10 ** 9) * 100  # перевод в [cm]
        epsO, epsS, lambdaS = Model.epsilon(T, Sw)
        y = lambdaS / lamda
        eps1 = epsO + (epsS - epsO) / (1 + y*y)
        eps2 = y * (epsS - epsO) / (1 + y*y)
        sigma = 0.00001 * (2.63 * T + 77.5) * Sw
        eps2 = eps2 + 60 * sigma * lamda
        return eps1 - 1j * eps2

    @staticmethod
    def M_horizontal(frequency: float, psi: float, T: float, Sw: float):
        epsilon = Model.epsilon_c(frequency, T, Sw)
        cos = np.sqrt(epsilon - np.cos(psi)*np.cos(psi))
        return (np.sin(psi) - cos) / (np.sin(psi) + cos)

    @staticmethod
    def M_vertical(frequency: float, psi: float, T: float, Sw: float):
        epsilon = Model.epsilon_c(frequency, T, Sw)
        cos = np.sqrt(epsilon - np.cos(psi) * np.cos(psi))
        return (epsilon * np.sin(psi) - cos) / (epsilon * np.sin(psi) + cos)

    @staticmethod
    def R_horizontal(frequency: float, theta: float, T: float, Sw: float):
        M_h = Model.M_horizontal(frequency, np.pi / 2. - theta, T, Sw)
        return np.absolute(M_h) ** 2

    @staticmethod
    def R_vertical(frequency: float, theta: float, T: float, Sw: float):
        M_v = Model.M_vertical(frequency, np.pi / 2. - theta, T, Sw)
        return np.absolute(M_v) ** 2

    @staticmethod
    def R(frequency: float, T: float, Sw: float):
        epsilon = Model.epsilon_c(frequency, T, Sw)
        return np.absolute((np.sqrt(epsilon) - 1) / (np.sqrt(epsilon) + 1)) ** 2

    def T_profile_10km(self, H, dh):
        return np.array([
            self.T - 6.5 * k * dh for k in range(int(H / dh) + 1)
        ])

    def P_profile_10km(self, H, dh):
        return np.array([
            self.P * math.exp(-k * dh / 7.7) for k in range(int(H / dh) + 1)
        ])

    def rho_profile_10km(self, H, dh):
        return np.array([
            self.rho * math.exp(-k * dh / 2.1) for k in range(int(H / dh) + 1)
        ])

    def get_profiles_10km(self, H, dh):
        return self.T_profile_10km(H, dh), self.P_profile_10km(H, dh), self.rho_profile_10km(H, dh)

    def Ig_down(self, freq, H, dh):
        Nz = int(H / dh) + 1
        T, P, rho = self.get_profiles_10km(H, dh)
        g = self.convert_dB2np(
            self.gammaOxygen(freq, T, P) +
            self.gammaWVapor(freq, T, P, rho)
        )
        Ig_down = lambda h: np.sum(g[1:h]) * dh + (g[0] + g[h]) / 2. * dh
        return Ig_down(Nz - 1)

    def Ig_up(self, freq, H, dh):
        T, P, rho = self.get_profiles_10km(H, dh)
        g = self.convert_dB2np(
            self.gammaOxygen(freq, T, P) +
            self.gammaWVapor(freq, T, P, rho)
        )
        Ig_up = lambda h: np.sum(g[h + 1:-1]) * dh + (g[h] + g[-1]) / 2. * dh
        return Ig_up(0)

    def T_avg_down(self, freq: float, H: float, dh: float) -> float:
        Nz = int(H / dh) + 1
        T, P, rho = self.get_profiles_10km(H, dh)
        g = self.convert_dB2np(
            self.gammaOxygen(freq, T, P) +
            self.gammaWVapor(freq, T, P, rho)
        )
        Ig_down = lambda h: np.sum(g[1:h]) * dh + (g[0] + g[h]) / 2. * dh
        f_down = lambda h: (T[h] + 273.15) * g[h] * np.exp(-Ig_down(h))
        Tb_down = dh * (f_down(0) + f_down(Nz - 1)) / 2.
        for k in range(1, Nz - 1):
            Tb_down += dh * f_down(k)
        Tb_down += self.TK * np.exp(-Ig_down(Nz - 1))
        # Tau = self.tau_theory(freq)
        # Tau = Ig_down(Nz - 1)
        Tau = np.sum(g[1:-1]) * dh + (g[0] + g[-1]) / 2. * dh
        return Tb_down / (1 - np.exp(-Tau))

    def T_avg_up(self, freq: float, H: float, dh: float) -> float:
        Nz = int(H / dh) + 1
        T, P, rho = self.get_profiles_10km(H, dh)
        g = self.convert_dB2np(
            self.gammaOxygen(freq, T, P) +
            self.gammaWVapor(freq, T, P, rho)
        )
        Ig_up = lambda h: np.sum(g[h+1:-1]) * dh + (g[h] + g[-1]) / 2. * dh
        f_up = lambda h: (T[h] + 273.15) * g[h] * np.exp(-Ig_up(h))
        Tb_up = dh * (f_up(0) + f_up(Nz - 1)) / 2.
        for k in range(1, Nz - 1):
            Tb_up += dh * f_up(k)
        # Tau = self.tau_theory(freq)
        # Tau = Ig_up(0)
        Tau = np.sum(g[1:-1]) * dh + (g[0] + g[-1]) / 2. * dh
        return Tb_up / (1 - np.exp(-Tau))
