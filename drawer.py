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
                 savefig_path='', axvlines=None, linestyles=None):
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

        for key in DATA.keys():

            T, V = [], []
            for t, v in DATA[key]:
                T.append(t)
                V.append(v)
                if t < min_t:
                    min_t = t
                if t > max_t:
                    max_t = t

            lst = ''
            try:
                l, c, w, m = labels[key], colors[key], linewidth, marker
                try:
                    lst = linestyles[key]
                except TypeError:
                    pass
            except KeyError:
                continue

            self.__plot(T, V, l, c, w, m, lst)

            plt.draw()
            plt.gcf().canvas.flush_events()

        for x in axvlines:
            plt.axvline(x=x, linewidth=0.5, linestyle=':', color='black')

        x_ticks_step = (max_t - min_t) / 10
        x_ticks_pos = [t for t in np.arange(min_t, max_t + x_ticks_step, x_ticks_step, dtype=float)]

        x_ticks_labels = [Double2TDateTime(t).strTime(timeformat)
                          for t in np.arange(min_t, max_t + x_ticks_step, x_ticks_step, dtype=float)]
        if timeformat == '!s':
            x_ticks_labels = [Double2TDateTime(t).strSeconds()
                              for t in np.arange(min_t, max_t + x_ticks_step, x_ticks_step, dtype=float)]

        plt.xticks(x_ticks_pos, x_ticks_labels, rotation=50, fontsize=10)

        self.ax.legend(loc='best',
                       # bbox_to_anchor=(0.7, 0.4),
                       # frameon=False
                       )

        plt.ioff()
        if savefig_path:
            plt.savefig(savefig_path, dpi=600)
        return

    def __plot(self, T, V, label, color, linewidth, marker, linestyle):
        m, w, lst = '', 1, '--'
        if marker:
            m = '+'
            lst = ''
        if linewidth:
            w = linewidth
        if linestyle:
            lst = linestyle
        self.ax.plot(T, V, label=label, color=color, linewidth=w, marker=m, linestyle=lst)
        return

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

