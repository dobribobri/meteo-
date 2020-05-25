# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

import math
from collections import OrderedDict
import numpy as np


class parameter:

    class freqs:
        all = [np.round(f, decimals=1) for f in np.arange(18.0, 27.3, 0.2)]

        basic = [18.0, 21.0, 22.0, 27.0]

        basic_plus = [18.0, 19.4, 22.2, 23.6, 25.8, 26.6]

        int_step = [np.round(f, decimals=0) for f in np.arange(18.0, 27.1, 1)]

        shifted = [np.round(f, decimals=1) for f in np.arange(21.2, 24.1, 0.2)]

        qw2_freq_pairs = [(18.0, 21.0), (18.0, 22.0), (21.0, 27.0), (22.0, 27.0)]

    class plot:
        linewidth = 1

        class colors:
            basic = {18.0: 'blue', 21.0: 'green', 22.0: 'orange', 27.0: 'red'}

            basic_plus = {18.0: 'darkblue', 19.4: 'dodgerblue', 22.2: 'darkorange',
                          23.6: 'forestgreen', 25.8: 'crimson', 26.6: 'red'}

            weather = {'temper': 'black', 'mmrtst': 'crimson', 'pr_hpa': 'red',
                       'rhorel': 'blue', 'rhoabs': 'darkblue', 'v_wind': 'darkorange',
                       'rainrt': 'forestgreen'}

            qw2 = {(18.0, 21.0): 'crimson',
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

            basic_plus = {18.0: additional_linestyles['densely dotted'],
                          19.4: '--',
                          22.2: additional_linestyles['solid'],
                          23.6: additional_linestyles['densely dashdotted'],
                          25.8: additional_linestyles['densely dashed'],
                          26.6: ':'}

        class textsubs:
            tb = [(0.6, 0.6, '1'), (0.5, 0.5, '2'), (0.5, 0.5, '3'), (0.5, 0.5, '4')]

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
                    return {'temper': r"Температура воздуха ($^\circ$C)",
                            'mmrtst': r"Атмосферное давление (мм.рт.ст)",
                            'pr_hpa': r"Атмосферное давление (гПа)",
                            'rhorel': r"Относительная влажность (%)",
                            'rhoabs': r"Абсолютная влажность (г/м$^3$)",
                            'v_wind': r"Скорость ветра (м/с)",
                            'rainrt': r"Количество осадков (мм)"}
                return {'temper': r"Air temperature, $^\circ$C",
                        'mmrtst': r"Atmospheric pressure, mmHg",
                        'pr_hpa': r"Atmospheric pressure, hPa",
                        'rhorel': r"Relative humidity, %",
                        'rhoabs': r"Absolute humidity, g/m$^3$",
                        'v_wind': r"Wind speed, m/sec",
                        'rainrt': r"Precipitation, mm"}

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
    class standart_conditions:
        T = 15  # cels
        P = 1013  # hPa
        rho = 7.5  # g/m^3
        Tavg = 1  # cels
        Tobl = -2  # cels

    class work:
        theta = (math.pi / 180) * 51  # rad

    class struct_func:
        thinning = 11
        part = 1 / 20

        rightShowLimit = 500 * 0.000011574

        class borland:
            @staticmethod
            def t_sec(sec: float):
                return sec * 0.000011574

    class parsing:

        class measurements:
            rm_zeros = True
            sort_freqs = True
            sort_time = False
            outliers_elimination = False
            upper_threshold_val = None
