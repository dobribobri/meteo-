# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from session import Session
from matplotlib import pyplot as plt
from borland_datetime import Double2TDateTime
import numpy as np
from termcolor import colored
from matplotlib import rc
rc('font', **{'family': 'serif'})
rc('text', usetex=True)
rc('text.latex', preamble=r"\usepackage[T2A]{fontenc}")
rc('text.latex', preamble=r"\usepackage[utf8]{inputenc}")
rc('text.latex', preamble=r"\usepackage[russian]{babel}")


class Drawer:
    def __init__(self):
        self.k = 0
        self.ax = None

    def draw(self, DATA: Session,
             title: str = '',
             xlabel: str = '', ylabel: str = '',
             labels: dict = None,
             colors: dict = None,
             linewidth: float = None,
             timeformat: str = 'hms+',
             marker: bool = False,
             savefig_path: str = None,
             axvlines: list = None,
             linestyles: dict = None,
             x_ticks_step: float = None) -> None:
        if axvlines is None:
            axvlines = []

        plt.ion()
        self.k += 1
        print(colored('Plot #{} - {} ...'.format(self.k, title), 'blue'))
        plt.figure(self.k)
        self.ax = plt.gca()
        self.ax.set_title(title, fontsize=11)
        self.ax.set_xlabel(xlabel, fontsize=10, fontweight='bold')
        self.ax.xaxis.set_label_coords(0.5, 0.04)
        self.ax.set_ylabel(ylabel, fontsize=11, rotation=90, fontweight='bold')
        min_t, max_t = DATA.get_time_bounds()

        for key in DATA.keys:
            w = linewidth
            m = marker

            try:
                l = labels[key]
            except KeyError:
                continue
            except TypeError:
                l = str(key)

            try:
                c = colors[key]
            except KeyError:
                continue
            except TypeError:
                c = 'black'

            try:
                s = linestyles[key]
            except KeyError:
                continue
            except TypeError:
                s = ''

            self.__plot(DATA.get_timestamps(key),
                        DATA.get_values(key),
                        l, c, w, m, s)
            plt.draw()
            plt.gcf().canvas.flush_events()

        for x in axvlines:
            plt.axvline(x=x, linewidth=0.5, linestyle=':', color='black')

        if not x_ticks_step:
            x_ticks_step = (max_t - min_t) / 10
        x_ticks_pos, x_ticks_labels = [], []
        for t in np.arange(min_t, max_t + x_ticks_step, x_ticks_step, dtype=float):
            x_ticks_pos.append(t)
            DT = Double2TDateTime(t)
            if timeformat == '!s':
                x_ticks_labels.append(DT.strSeconds())
            else:
                x_ticks_labels.append(DT.strTime(timeformat))

        plt.xticks(x_ticks_pos, x_ticks_labels, rotation=50, fontsize=10)

        self.ax.legend(loc='best')

        plt.ioff()
        if savefig_path is not None:
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
