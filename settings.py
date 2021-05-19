# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

import math
from collections import OrderedDict
import numpy as np
import os

radiometerName: str = 'P22M'

LT: str = 'temper'
LT_K: str = 't_kelv'
LT_C: str = 't_cels'
LP: str = 'pressu'
LP_mm: str = 'mmrtst'
LP_hpa: str = 'pr_hpa'
Lrho_rel: str = 'rhorel'
Lrho_abs: str = 'rhoabs'
LVwind: str = 'v_wind'
LRainRt: str = 'rainrt'


class Settings:
    # Be careful! Do not set '/' path
    meteoBaseDir: str = './w/'
    radiometerPrefix: str = radiometerName
    bfdataDir: str = './bf/'
    tfdataDir: str = './tf/'
    cfdataDir: str = './cf/'
    calibrPrefix: str = 'calibr23'
    calibrPostfix: str = 'p22m'

    swvapour_conf_path: str = './saturated_wvpr.conf'

    class Plots:
        PlotRoot: str = './pic/'
        TbPlotDir: str = os.path.join(PlotRoot, 'tb/')
        WeatherPlotDir: str = os.path.join(PlotRoot, 'weather/')
        SFPlotDir: str = os.path.join(PlotRoot, 'sf/')
        QWPlotDir: str = os.path.join(PlotRoot, 'qw/')

        @staticmethod
        def refresh(_PlotRoot: str) -> None:
            Settings.Plots.PlotRoot = _PlotRoot
            Settings.Plots.TbPlotDir = os.path.join(_PlotRoot, 'tb/')
            Settings.Plots.WeatherPlotDir = os.path.join(_PlotRoot, 'weather/')
            Settings.Plots.SFPlotDir = os.path.join(_PlotRoot, 'sf/')
            Settings.Plots.QWPlotDir = os.path.join(_PlotRoot, 'qw/')

    class Reports:
        ReportRoot: str = './reports/'
        TbReportDir: str = os.path.join(ReportRoot, 'tb/')
        WeatherReportDir: str = os.path.join(ReportRoot, 'weather/')
        SFReportDir: str = os.path.join(ReportRoot, 'sf/')
        QWReportDir: str = os.path.join(ReportRoot, 'qw/')

        @staticmethod
        def refresh(_ReportRoot: str) -> None:
            Settings.Reports.ReportRoot = _ReportRoot
            Settings.Reports.TbReportDir = os.path.join(_ReportRoot, 'tb/')
            Settings.Reports.WeatherReportDir = os.path.join(_ReportRoot, 'weather/')
            Settings.Reports.SFReportDir = os.path.join(_ReportRoot, 'sf/')
            Settings.Reports.QWReportDir = os.path.join(_ReportRoot, 'qw/')

    class Server:
        IP: str = '217.107.96.189'
        login: str = 'ftprad'
        password: str = 'radireftp'

        measurementsRoot: str = os.path.join('/home/rad/', radiometerName)
        year_path: dict = {2021: measurementsRoot,
                           2020: os.path.join(measurementsRoot, '2020/'),
                           2019: os.path.join(measurementsRoot, '2019/'),
                           2018: os.path.join(measurementsRoot, '2018/'),
                           2017: os.path.join(measurementsRoot, '2017/')}

        calibrRoot: str = os.path.join('/home/rad/', radiometerName, 'calibr/')

    class Markup:
        class Old:
            categories: dict = {1: 'ncl', 2: 'cl1-', 3: 'cl2-', 4: 'cl1+', 5: 'cl2+', 6: 'mix', 7: 'badw'}

            summerCategories: dict = {1: 'sncl', 2: 'sclm1', 3: 'sclm2', 4: 'sclp1', 5: 'sclp2', 6: 'smix', 7: 'sbadw'}
            winterCategories: dict = {1: 'wncl', 2: 'wclm1', 3: 'wclm2', 4: 'wclp1', 5: 'wclp2', 6: 'wmix', 7: 'wbadw'}

        categories: dict = {1: 'N cl', 2: 'Cu hum', 3: 'Cu med', 4: 'Cu cong', 5: 'Cb', 6: 'Cb+',
                            7: 'St', 8: 'St+', 9: 'Sc', 10: 'Ns', 11: 'Ns+'}

        summerCategories: dict = {1: 'N cl', 2: 'Cu hum', 3: 'Cu med', 4: 'Cu cong', 5: 'Cb+', 6: 'Sc', 7: 'Ns+'}
        winterCategories: dict = {1: 'N cl', 2: 'Cu med', 3: 'St', 4: 'St+', 5: 'Sc'}


class parameter:

    class weather:

        class labels:
            T: str = LT
            T_K: str = LT_K
            T_C: str = LT_C
            P: str = LP
            P_mm: str = LP_mm
            P_hpa: str = LP_hpa
            rho_rel: str = Lrho_rel
            rho_abs: str = Lrho_abs
            Vwind: str = LVwind
            RainRt: str = LRainRt

    class freqs:
        all: list = [np.round(f, decimals=1) for f in np.arange(18.0, 27.3, 0.2)]

        basic: list = [18.0, 21.0, 22.0, 27.0]

        basic_plus: list = [18.0, 19.4, 22.2, 23.6, 25.8, 26.6]

        int_step: list = [np.round(f, decimals=0) for f in np.arange(18.0, 27.1, 1)]

        shifted: list = [np.round(f, decimals=1) for f in np.arange(21.2, 24.1, 0.2)]

        qw2_freq_pairs: list = [(18.0, 21.0), (18.0, 22.0), (21.0, 27.0), (22.0, 27.0)]

    class plot:
        linewidth: float = 1

        class colors:
            basic: dict = {18.0: 'blue', 21.0: 'green', 22.0: 'orange', 27.0: 'red'}

            basic_plus: dict = {18.0: 'darkblue', 19.4: 'dodgerblue', 22.2: 'darkorange',
                                23.6: 'forestgreen', 25.8: 'crimson', 26.6: 'red'}

            weather: dict = {LT: 'black', LT_C: 'black', LT_K: 'black',
                             LP: 'crimson', LP_mm: 'crimson', LP_hpa: 'red',
                             Lrho_rel: 'blue', Lrho_abs: 'darkblue', LVwind: 'darkorange',
                             LRainRt: 'forestgreen'}

            qw2: dict = {(18.0, 21.0): 'crimson',
                         (18.0, 22.0): 'forestgreen',
                         (21.0, 27.0): 'darkorange',
                         (22.0, 27.0): 'darkblue'}

        class linestyles:
            additional_linestyles = OrderedDict(
                [('solid', (0, ())),
                 ('loosely dotted', (0, (1, 10))),
                 ('dotted', (0, (1, 5))),
                 ('densely dotted', (0, (1, 1))),

                 ('loosely dashed', (0, (5, 10))),
                 ('dashed', (0, (5, 5))),
                 ('densely dashed', (0, (5, 1))),

                 ('loosely dashdotted', (0, (3, 10, 1, 10))),
                 ('dashdotted', (0, (3, 5, 1, 5))),
                 ('densely dashdotted', (0, (3, 1, 1, 1))),

                 ('loosely dashdotdotted', (0, (3, 10, 1, 10, 1, 10))),
                 ('dashdotdotted', (0, (3, 5, 1, 5, 1, 5))),
                 ('densely dashdotdotted', (0, (3, 1, 1, 1, 1, 1)))])

            basic_plus: dict = {18.0: additional_linestyles['densely dotted'],
                                19.4: '--',
                                22.2: additional_linestyles['solid'],
                                23.6: additional_linestyles['densely dashdotted'],
                                25.8: additional_linestyles['densely dashed'],
                                26.6: ':'}

        class labels:
            def __init__(self, language: str):
                self.lang = language

            def __a(self, l_freqs, numb=False):
                l_dict = {}
                for i, f in enumerate(l_freqs):
                    f = np.round(f, decimals=1)
                    ghz = 'GHz'
                    if self.lang == 'ru':
                        ghz = u'ГГц'
                    if numb:
                        l_dict[f] = '({}) {} {}'.format(i + 1, f, ghz)
                    else:
                        l_dict[f] = '{} {}'.format(f, ghz)
                return l_dict

            @property
            def all(self):
                return self.__a(np.arange(18.0, 27.3, 0.2))

            @property
            def basic(self):
                return self.__a([18.0, 21.0, 22.0, 27.0])

            @property
            def basic_plus(self):
                return self.__a([18.0, 19.4, 22.2, 23.6, 25.8, 26.6], numb=True)

            @property
            def weather(self):
                if self.lang == 'ru':
                    return {LT: r"Температура воздуха",
                            LT_C: r"Температура воздуха ($^\circ$C)",
                            LT_K: r"Температура воздуха ($^\circ$K)",
                            LP: r"Атмосферное давление",
                            LP_mm: r"Атмосферное давление (мм.рт.ст)",
                            LP_hpa: r"Атмосферное давление (гПа)",
                            Lrho_rel: r"Относительная влажность (%)",
                            Lrho_abs: r"Абсолютная влажность (г/м$^3$)",
                            LVwind: r"Скорость ветра (м/с)",
                            LRainRt: r"Количество осадков (мм)"}
                return {LT: r"Air temperature",
                        LT_C: r"Air temperature, $^\circ$C",
                        LT_K: r"Air temperature, $^\circ$K",
                        LP: r"Atmospheric pressure",
                        LP_mm: r"Atmospheric pressure, mmHg",
                        LP_hpa: r"Atmospheric pressure, hPa",
                        Lrho_rel: r"Relative humidity, %",
                        Lrho_abs: r"Absolute humidity, g/m$^3$",
                        LVwind: r"Wind speed, m/sec",
                        LRainRt: r"Precipitation, mm"}

            @property
            def qw2(self):
                if self.lang == 'ru':
                    return {(18.0, 21.0): u'18 и 21 ГГц',
                            (18.0, 22.0): u'18 и 22 ГГц',
                            (21.0, 27.0): u'21 и 27 ГГц',
                            (22.0, 27.0): u'22 и 27 ГГц'}
                return {(18.0, 21.0): '18, 21 GHz',
                        (18.0, 22.0): '18, 22 GHz',
                        (21.0, 27.0): '21, 27 GHz',
                        (22.0, 27.0): '22, 27 GHz'}

    # стандартные условия
    class standard_conditions:
        T: float = 15  # cels
        P: float = 1013  # hPa
        rho: float = 7.5  # g/m^3
        Tavg: float = 1  # cels
        Tobl: float = -2  # cels

    class work:
        # theta: float = (math.pi / 180) * 51  # rad
        theta: float = 0.

    class struct_func:
        t_step: float = None
        part: float = 1./20.

        rightShowLimit: float = 500    # sec

    class parsing:

        class measurements:
            rm_zeros: bool = True
            sort_freqs: bool = True
            sort_time: bool = False
            outliers_elimination: bool = False
            upper_threshold_val: bool = None
