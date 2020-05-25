# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

import math
from collections import OrderedDict


class parameter:

    class freqs:
        ALL = [
            18.0, 18.2, 18.4, 18.6, 18.8,
            19.0, 19.2, 19.4, 19.6, 19.8,
            20.0, 20.2, 20.4, 20.6, 20.8,
            21.0, 21.2, 21.4, 21.6, 21.8,
            22.0, 22.2, 22.4, 22.6, 22.8,
            23.0, 23.2, 23.4, 23.6, 23.8,
            24.0, 24.2, 24.4, 24.6, 24.8,
            25.0, 25.2, 25.4, 25.6, 25.8,
            26.0, 26.2, 26.4, 26.6, 26.8,
            27.0, 27.2
            ]

        BASIC = [18.0, 21.0, 22.0, 27.0]

        # BASIC_PLUS = [18.0, 19.4, 22.2, 23.6, 25.8, 27.2]
        BASIC_PLUS = [18.0, 19.4, 22.2, 23.6, 25.8, 26.6]

        INT_STEP = [18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0]

        SHIFTED = [
            21.2, 21.4, 21.6, 21.8, 22.0,
            22.2, 22.4, 22.6, 22.8, 23.0,
            23.2, 23.4, 23.6, 23.8, 24.0
        ]

        QW2_FREQ_PAIRS = [(18.0, 21.0), (18.0, 22.0), (21.0, 27.0), (22.0, 27.0)]

        QW2a_FREQ_PAIRS = [(18.0, 22.0), (18.2, 22.2), (18.4, 22.4), (18.6, 22.6), (18.8, 22.8),
                           (21.0, 27.0), (21.2, 27.2)]

    class plot:
        linewidth = 1

        class colors:

            BASIC = {18.0: 'blue', 21.0: 'green', 22.0: 'orange', 27.0: 'red'}

            # BASIC_PLUS = {18.0: 'darkblue', 19.4: 'dodgerblue', 22.2: 'darkorange',
            #               23.6: 'forestgreen', 25.8: 'crimson', 27.2: 'red'}
            BASIC_PLUS = {18.0: 'darkblue', 19.4: 'dodgerblue', 22.2: 'darkorange',
                          23.6: 'forestgreen', 25.8: 'crimson', 26.6: 'red'}
            # BASIC_PLUS = {18.0: 'black', 19.4: 'black', 22.2: 'black',
            #               23.6: 'black', 25.8: 'black', 26.6: 'black'}

            WEATHER = {'temper': 'black', 'mmrtst': 'crimson', 'pr_hpa': 'red',
                       'rhorel': 'blue', 'rhoabs': 'darkblue',
                       'v_wind': 'darkorange', 'rainrt': 'forestgreen'}

            QW2 = {(18.0, 21.0): 'crimson',
                   (18.0, 22.0): 'forestgreen',
                   (21.0, 27.0): 'darkorange',
                   (22.0, 27.0): 'darkblue'}

            QW2a = {(18.0, 22.0): 'red',
                    (18.2, 22.2): 'crimson',
                    (18.4, 22.4): 'orangered',
                    (18.6, 22.6): 'orange',
                    (18.8, 22.8): 'darkorange',
                    (21.0, 27.0): 'forestgreen',
                    (21.2, 27.2): 'darkblue'}

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

            BASIC_PLUS = {18.0: additional_linestyles['densely dotted'],
                          19.4: '--',
                          22.2: additional_linestyles['solid'],
                          23.6: additional_linestyles['densely dashdotted'],
                          25.8: additional_linestyles['densely dashed'],
                          26.6: ':'}

        class textsubs:
            tb = [(0.6, 0.6, '1'), (0.5, 0.5, '2'), (0.5, 0.5, '3'), (0.5, 0.5, '4')]


        class labels:

            ALL = {18.0: '18.0 GHz', 18.2: '18.2 GHz', 18.4: '18.4 GHz', 18.6: '18.6 GHz', 18.8: '18.8 GHz',
            19.0: '19.0 GHz', 19.2: '19.2 GHz', 19.4: '19.4 GHz', 19.6: '19.6 GHz', 19.8: '19.8 GHz',
            20.0: '20.0 GHz', 20.2: '20.2 GHz', 20.4: '20.4 GHz', 20.6: '20.6 GHz', 20.8: '20.8 GHz',
            21.0: '21.0 GHz', 21.2: '21.2 GHz', 21.4: '21.4 GHz', 21.6: '21.6 GHz', 21.8: '21.8 GHz',
            22.0: '22.0 GHz', 22.2: '22.2 GHz', 22.4: '22.4 GHz', 22.6: '22.6 GHz', 22.8: '22.8 GHz',
            23.0: '23.0 GHz', 23.2: '23.2 GHz', 23.4: '23.4 GHz', 23.6: '23.6 GHz', 23.8: '23.8 GHz',
            24.0: '24.0 GHz', 24.2: '24.2 GHz', 24.4: '24.4 GHz', 24.6: '24.6 GHz', 24.8: '24.8 GHz',
            25.0: '25.0 GHz', 25.2: '25.2 GHz', 25.4: '25.4 GHz', 25.6: '25.6 GHz', 25.8: '25.8 GHz',
            26.0: '26.0 GHz', 26.2: '26.2 GHz', 26.4: '26.4 GHz', 26.6: '26.6 GHz', 26.8: '26.8 GHz',
            27.0: '27.0 GHz', 27.2: '27.2 GHz'}

            BASIC = {18.0: '18 GHz', 21.0: '21 GHz', 22.0: '22 GHz', 27.0: '27 GHz'}

            # BASIC_PLUS = {18.0: '18.0 GHz', 19.4: '19.4 GHz', 22.2: '22.2 GHz',
            #               23.6: '23.6 GHz', 25.8: '25.8 GHz', 27.2: '27.2 GHz'}

            BASIC_PLUS = {18.0: u'(1) 18.0 GHz', 19.4: u'(2) 19.4 GHz', 22.2: u'(3) 22.2 GHz',
                          23.6: u'(4) 23.6 GHz', 25.8: u'(5) 25.8 GHz', 26.6: u'(6) 26.6 GHz'}

            # BASIC_PLUS = {18.0: '1. 18.0 GHz', 19.4: '2. 19.4 GHz', 22.2: '3. 22.2 GHz',
            #               23.6: '4. 23.6 GHz', 25.8: '5. 25.8 GHz', 26.6: '6. 26.6 GHz'}

            WEATHER = {'temper': "Air temperature", 'mmrtst': "Atmospheric pressure",
                       'pr_hpa': "Atmospheric pressure",
                       'rhorel': "Relative humidity", 'rhoabs': "Absolute humidity",
                       'v_wind': "Wind speed", 'rainrt': "Precipitation"}

            QW2 = {(18.0, 21.0): '18, 21 GHz',
                   (18.0, 22.0): '18, 22 GHz',
                   (21.0, 27.0): '21, 27 GHz',
                   (22.0, 27.0): '22, 27 GHz'}

            QW2a = {(18.0, 22.0): '18.0, 22.0 GHz',
                    (18.2, 22.2): '18.2, 22.2 GHz',
                    (18.4, 22.4): '18.4, 22.4 GHz',
                    (18.6, 22.6): '18.6, 22.6 GHz',
                    (18.8, 22.8): '18.8, 22.8 GHz',
                    (21.0, 27.0): '21.0, 27.0 GHz',
                    (21.2, 27.2): '21.2, 27.2 GHz'}

            class rus:
                ALL = {18.0: u'18.0 ГГц', 18.2: u'18.2 ГГц', 18.4: u'18.4 ГГц', 18.6: u'18.6 ГГц', 18.8: u'18.8 ГГц',
                       19.0: u'19.0 ГГц', 19.2: u'19.2 ГГц', 19.4: u'19.4 ГГц', 19.6: u'19.6 ГГц', 19.8: u'19.8 ГГц',
                       20.0: u'20.0 ГГц', 20.2: u'20.2 ГГц', 20.4: u'20.4 ГГц', 20.6: u'20.6 ГГц', 20.8: u'20.8 ГГц',
                       21.0: u'21.0 ГГц', 21.2: u'21.2 ГГц', 21.4: u'21.4 ГГц', 21.6: u'21.6 ГГц', 21.8: u'21.8 ГГц',
                       22.0: u'22.0 ГГц', 22.2: u'22.2 ГГц', 22.4: u'22.4 ГГц', 22.6: u'22.6 ГГц', 22.8: u'22.8 ГГц',
                       23.0: u'23.0 ГГц', 23.2: u'23.2 ГГц', 23.4: u'23.4 ГГц', 23.6: u'23.6 ГГц', 23.8: u'23.8 ГГц',
                       24.0: u'24.0 ГГц', 24.2: u'24.2 ГГц', 24.4: u'24.4 ГГц', 24.6: u'24.6 ГГц', 24.8: u'24.8 ГГц',
                       25.0: u'25.0 ГГц', 25.2: u'25.2 ГГц', 25.4: u'25.4 ГГц', 25.6: u'25.6 ГГц', 25.8: u'25.8 ГГц',
                       26.0: u'26.0 ГГц', 26.2: u'26.2 ГГц', 26.4: u'26.4 ГГц', 26.6: u'26.6 ГГц', 26.8: u'26.8 ГГц',
                       27.0: u'27.0 ГГц', 27.2: u'27.2 ГГц'}

                BASIC = {18.0: u'18 ГГц', 21.0: u'21 ГГц', 22.0: u'22 ГГц', 27.0: u'27 ГГц'}

                # BASIC_PLUS = {18.0: u'18.0 ГГц', 19.4: u'19.4 ГГц', 22.2: u'22.2 ГГц',
                #               23.6: u'23.6 ГГц', 25.8: u'25.8 ГГц', 27.2: u'27.2 ГГц'}
                BASIC_PLUS = {18.0: u'(1) 18.0 ГГц', 19.4: u'(2) 19.4 ГГц', 22.2: u'(3) 22.2 ГГц',
                              23.6: u'(4) 23.6 ГГц', 25.8: u'(5) 25.8 ГГц', 26.6: u'(6) 26.6 ГГц'}

                WEATHER = {'temper': r"Температура воздуха ($^\circ$C)", 'mmrtst': u"Атмосферное давление (мм.рт.ст)",
                           'pr_hpa': u"Атмосферное давление (гПа)",
                           'rhorel': u"Относительная влажность (%)", 'rhoabs': r"Абсолютная влажность (г/м$^3$)",
                           'v_wind': u"Скорость ветра (м/с)", 'rainrt': u"Количество осадков (мм)"}

                QW2 = {(18.0, 21.0): u'18 и 21 ГГц',
                       (18.0, 22.0): u'18 и 22 ГГц',
                       (21.0, 27.0): u'21 и 27 ГГц',
                       (22.0, 27.0): u'22 и 27 ГГц'}

                QW2a = {(18.0, 22.0): '18.0, 22.0 ГГц',
                        (18.2, 22.2): '18.2, 22.2 ГГц',
                        (18.4, 22.4): '18.4, 22.4 ГГц',
                        (18.6, 22.6): '18.6, 22.6 ГГц',
                        (18.8, 22.8): '18.8, 22.8 ГГц',
                        (21.0, 27.0): '21.0, 27.0 ГГц',
                        (21.2, 27.2): '21.2, 27.2 ГГц'}

    # стандартные условия
    class standart_condirions:
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

        t25sec = 25 * 0.000011574
        t30sec = 30 * 0.000011574
        t50sec = 50 * 0.000011574
        t100sec = 100 * 0.000011574
        t150sec = 150 * 0.000011574
        t200sec = 200 * 0.000011574
        t250sec = 250 * 0.000011574

    class parsing:

        class measurements:
            rm_zeros = True
            sort_freqs = True
            sort_time = False
            outliers_elimination = False
            threshold_percentage = None
            upper_threshold_val = None
