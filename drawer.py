# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from matplotlib import pyplot as plt
from borland.datetime import Double2TDateTime
import sys
import numpy as np
# from matplotlib.ticker import FormatStrFormatter
from termcolor import colored
from matplotlib import rc
rc('font', **{'family': 'serif'})
rc('text', usetex=True)
rc('text.latex', unicode=True)
rc('text.latex', preamble=r"\usepackage[T2A]{fontenc}")
rc('text.latex', preamble=r"\usepackage[utf8]{inputenc}")
rc('text.latex', preamble=r"\usepackage[russian]{babel}")


class Drawer:
    def __init__(self):
        self.k = 0
        self.ax = None

    def drawDATA(self, DATA, title='', xlabel='', ylabel='',
                 labels=None, colors=None, linewidth=None,
                 timeformat='hms+', marker=False,
                 savefig_path='', axvlines=None, linestyles=None, textsubs=None):
        if axvlines is None:
            axvlines = []
        plt.ion()
        self.k += 1
        print(colored('График #{} - {} ...'.format(self.k, title), 'blue'))
        plt.figure(self.k)
        self.ax = plt.gca()
        self.ax.set_title(title, fontsize=11)
        self.ax.set_xlabel(xlabel, fontsize=10, fontweight='bold')
        self.ax.xaxis.set_label_coords(0.5, 0.04)
        self.ax.set_ylabel(ylabel, fontsize=11, rotation=90, fontweight='bold')
        min_t, max_t = sys.maxsize, 0
        # ax.xaxis.set_major_formatter(FormatStrFormatter('%0.1f'))
        # print(DATA)
        for key in DATA.keys():
            # print('key: {}'.format(key))
            T, V = [], []
            for t, v in DATA[key]:
                T.append(t)
                V.append(v)
                if t < min_t:
                    min_t = t
                if t > max_t:
                    max_t = t
            # print(T)
            # print(linestyles)
            l_st = ''
            try:
                l, c, w, m = labels[key], colors[key], linewidth, marker
                try:
                    l_st = linestyles[key]
                except TypeError:
                    pass
            except KeyError:
                continue

            self.__plot(T, V, l, c, w, m, l_st)

            plt.draw()
            plt.gcf().canvas.flush_events()

        for x in axvlines:
            plt.axvline(x=x, linewidth=0.5, linestyle=':', color='black')

        # print(min_t, max_t)
        x_ticks_step = (max_t - min_t) / 10
        x_ticks_pos = [t for t in np.arange(min_t, max_t + x_ticks_step, x_ticks_step, dtype=float)]
        # print(x_ticks_pos)
        x_ticks_labels = [Double2TDateTime(t).strTime(*Drawer.__timeformat_parser(timeformat))
                          for t in np.arange(min_t, max_t + x_ticks_step, x_ticks_step, dtype=float)]
        if timeformat == '!s':
            x_ticks_labels = [Double2TDateTime(t).strSeconds()
                              for t in np.arange(min_t, max_t + x_ticks_step, x_ticks_step, dtype=float)]

        plt.xticks(x_ticks_pos, x_ticks_labels, rotation=50, fontsize=10)

        self.ax.legend(loc='best',
                       # bbox_to_anchor=(0.7, 0.4),
                       # frameon=False
                       )

        # print(textsubs)
        # if textsubs:
        #     for item in textsubs:
        #         plt.text(*item)

        plt.ioff()
        if savefig_path:
            plt.savefig(savefig_path, dpi=600)
        return

    def __plot(self, T, V, label, color, linewidth, marker, linestyle):
        l, c, w, m, l_st = label, color, linewidth, marker, linestyle
        if l and c and w and l_st:
            self.ax.plot(T, V, label=l, color=c, linewidth=w, linestyle=l_st)
            return
        if l and c and w and m:
            self.ax.plot(T, V, label=l, color=c, linewidth=w, marker='+', linestyle='')
        if l and c and not w and m:
            self.ax.plot(T, V, label=l, color=c, marker='+', linestyle='')
        if l and not c and w and m:
            self.ax.plot(T, V, label=l, linewidth=w, marker='+', linestyle='')
        if l and not c and not w and m:
            self.ax.plot(T, V, label=l, marker='+', linestyle='')
        if not l and c and w and m:
            self.ax.plot(T, V, color=c, linewidth=w, marker='+', linestyle='')
        if not l and c and not w and m:
            self.ax.plot(T, V, color=c, marker='+', linestyle='')
        if not l and not c and w and m:
            self.ax.plot(T, V, linewidth=w, marker='+', linestyle='')
        if not l and not c and not w and m:
            self.ax.plot(T, V, marker='+', linestyle='')
        if l and c and w and not m:
            self.ax.plot(T, V, label=l, color=c, linewidth=w)
        if l and c and not w and not m:
            self.ax.plot(T, V, label=l, color=c)
        if l and not c and w and not m:
            self.ax.plot(T, V, label=l, linewidth=w)
        if l and not c and not w and not m:
            self.ax.plot(T, V, label=l)
        if not l and c and w and not m:
            self.ax.plot(T, V, color=c, linewidth=w)
        if not l and c and not w and not m:
            self.ax.plot(T, V, color=c)
        if not l and not c and w and not m:
            self.ax.plot(T, V, linewidth=w)
        if not l and not c and not w and not m:
            self.ax.plot(T, V)
        return

    @staticmethod
    def __timeformat_parser(timeformat: str):
        hours, minutes, seconds, milliseconds = False, False, False, False
        for char in timeformat:
            if char == 'h':
                hours = True
            if char == 'm':
                minutes = True
            if char == 's':
                seconds = True
            if char == '+':
                milliseconds = True
        return hours, minutes, seconds, milliseconds

    @staticmethod
    def show():
        plt.show()
        plt.close()
        return

    @staticmethod
    def pause(interval: int = 1):
        plt.pause(interval)
        plt.close()
        return

