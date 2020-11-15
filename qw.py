# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from typing import Tuple
from measurement import Measurement
from weather import Weather
from settings import parameter as p
from p676 import Model
from session import Session, Series, Point
import numpy as np
import math
import sys
from matplotlib import pyplot as plt
from borland_datetime import TDateTime
from matplotlib import rc
rc('font', **{'family': 'serif'})
rc('text', usetex=True)
rc('text.latex', preamble=r"\usepackage[T2A]{fontenc}")
rc('text.latex', preamble=r"\usepackage[utf8]{inputenc}")
rc('text.latex', preamble=r"\usepackage[russian]{babel}")


class MoistureContent:
    def __init__(self, measurement: Measurement, weather: Weather,
                 Tavg: float = 5, Tcl: float = -2,
                 theta: float = p.work.theta):
        """
        :param measurement: Measurement object.
        :param weather: Weather object.
        :param Tavg: Average (effective) temperature of atmosphere (Cels).
        :param Tcl: Average cloud temperature (Cels).
        :param theta: Observation angle (degrees).
        """
        self.t_avg = Tavg + 273
        self.tcl = Tcl
        self.theta = theta
        self.m = measurement
        self.w = weather

    def tpwv_standard(self, t_step: float = None, Hrho: float = 1.8, smooth: int = 0) -> Session:
        session = self.m.DATA.copy()
        session.thin_fast(t_step)
        session.box()
        timestamps = session.get_timestamps_averaged()
        out = Session()
        for i in range(smooth, len(timestamps)):
            t = timestamps[i]
            hum = self.w.Rho_abs(t)
            for j in range(i - smooth, i):
                hum += self.w.Rho_abs(timestamps[j])
            hum /= (smooth + 1)
            out.add('q', Point(t, Model.Q(rho0=hum, Hrho=Hrho)))
        return out

    def liquidWater_spectral(self, frequencies: list = None,
                             t_step: float = None, w_step: float = 0.01) -> Session:
        print("Liquid water content evaluation...")
        if not frequencies:
            frequencies = self.m.DATA.keys
        session = self.m.DATA.select(frequencies)
        session.thin_fast(t_step)
        session.box()
        timestamps = session.get_timestamps_averaged()
        out = Session()
        model = Model(theta=0)
        for j, t in enumerate(timestamps):
            print('{:.2f}%'.format(j/len(timestamps)*100), end='\r', flush=True)
            spec = session.get_spectrum(t)
            T = self.w.Temperature(t, dimension=p.weather.labels.T_C)
            P = self.w.Pressure(t, dimension=p.weather.labels.P_hpa)
            hum = self.w.Rho_abs(t)
            model.setParameters(temperature=T, pressure=P, rho=hum)
            w_ = [max(model.opacity(brt, Tavg=self.t_avg) - model.tau_theory(f), 0) /
                  model.kw(f, tcl=self.tcl)
                  for f, brt in spec]
            w_max = np.max(w_)
            w_min = np.min(w_)
            minimal, W = sys.maxsize, 0.
            for w in np.arange(w_min, w_max + w_step, w_step):
                rms = math.sqrt(
                    sum(
                        [(model.opacity(brt, Tavg=self.t_avg) -
                          model.tau_theory(f) -
                          model.kw(f, tcl=self.tcl) * w) ** 2
                         for f, brt in spec]
                    )
                )
                if rms < minimal:
                    minimal = rms
                    W = w
            out.add('w', Point(t, W))

            # ANALYSIS
            # if 49 <= j < 60:
            #     plt.figure(876342 + j)
            #     plt.title(TDateTime.fromDouble(t).strTime('hm'))
            #     plt.plot(frequencies, [model.tau_theory(f) for f in frequencies],
            #              color='darkblue', linestyle='-.',
            #              label=r'$\tau(\nu)$')
            #     plt.plot(frequencies, [model.opacity(brt, self.t_avg) for _, brt in spec],
            #              color='forestgreen',
            #              label=r'$\ln(T_{avg}^{\nu}) - \ln(T_{avg}^{\nu} - T_b(\nu))$')
            #     plt.plot(frequencies, [model.tau_theory(f) + model.kw(f, self.tcl) * w_min
            #                            for f in frequencies],
            #              color='crimson', linestyle=':',
            #              label=r'$\tau(\nu) + k_w(\nu, T_{cl})\cdot ' + '{:.2f}$'.format(w_min))
            #     plt.plot(frequencies, [model.tau_theory(f) + model.kw(f, self.tcl) * w_max
            #                            for f in frequencies],
            #              color='crimson', linestyle='--',
            #              label=r'$\tau(\nu) + k_w(\nu, T_{cl})\cdot ' + '{:.2f}$'.format(w_max))
            #     plt.plot(frequencies, [model.tau_theory(f) + model.kw(f, self.tcl) * W
            #                            for f in frequencies],
            #              color='crimson', linestyle='-',
            #              label=r'$\tau(\nu) + k_w(\nu, T_{cl})\cdot ' + '{:.2f}$'.format(W))
            #     plt.legend(loc='best')

        print('100%   ', flush=True)
        return out

    def Spectral(self, frequencies: list = None,
                 t_step: float = None,
                 q_step: float = None,
                 w_step: float = 0.01) -> Tuple[Session, Session]:
        print("Moisture content evaluation (spectral method)...")
        if not frequencies:
            frequencies = self.m.DATA.keys
        session = self.m.DATA.select(frequencies)
        session.thin_fast(t_step)
        session.box()
        timestamps = session.get_timestamps_averaged()
        model = Model(theta=0)
        session_q, session_w = Session(), Session()
        for j, t in enumerate(timestamps):
            # if not(290 < j < 310):
            #     continue
            print('{:.2f}%'.format(j/len(timestamps)*100), end='\r', flush=True)
            spec = session.get_spectrum(t)
            T = self.w.Temperature(t, dimension=p.weather.labels.T_C)
            P = self.w.Pressure(t, dimension=p.weather.labels.P_hpa)
            hum = self.w.Rho_abs(t)
            model.setParameters(temperature=T, pressure=P, rho=hum)
            q_min = Model.Q(rho0=hum)
            q_max = max([(model.opacity(brt, Tavg=self.t_avg) - model.tauO_theory(f)) / model.krho(f)
                         for f, brt in spec])
            minimal, Q, W = sys.maxsize, q_min, 0.
            if not q_step:
                q_step_ = max((q_max - q_min) / 10., 0.1)
            else:
                q_step_ = q_step
            for q in np.arange(q_min, q_max + q_step_, q_step_):
                w_ = [max(
                          model.opacity(brt, Tavg=self.t_avg) - model.tauO_theory(f) - model.krho(f) * q,
                          0
                      ) / model.kw(f, tcl=self.tcl)
                      for f, brt in spec]
                w_max = np.max(w_)
                w_min = np.min(w_)
                for w in np.arange(w_min, w_max + w_step, w_step):
                    rms = math.sqrt(
                        sum(
                            [(model.opacity(brt, Tavg=self.t_avg) -
                              model.tauO_theory(f) - model.krho(f) * q -
                              model.kw(f, tcl=self.tcl) * w) ** 2
                             for f, brt in spec]
                        )
                    )
                    if rms < minimal:
                        minimal = rms
                        Q, W = q, w
            session_q.add('q', Point(t, Q))
            session_w.add('w', Point(t, W))

            # ANALYSIS
            # plt.figure(100000 + j)
            # plt.title('{} UTC+3 (MSK)\n'.format(TDateTime.fromDouble(t).strTime('hms')) +
            #           r'$T_0 = {:.1f}'.format(T) + r'^{\circ}$C, ' +
            #           r'$P_0 = {:.1f}$'.format(P/1.333) + ' мм.рт.ст., ' +
            #           r'$\rho_0 = {:.2f}$'.format(hum) + ' г/м$^3$')
            # plt.xlabel(r'Частота $\nu$, ГГц')
            # plt.ylabel('Поглощение, неперы')
            # plt.plot(frequencies, [model.tau_theory(f) for f in frequencies],
            #          color='darkblue', linestyle=':',
            #          label=r'(1) $\tau_{O_2}(\nu) + \tau_{\rho}(\nu),~$ Rec. ITU-R P676')
            # plt.plot(frequencies, [model.tauO_theory(f) +
            #                        model.krho(f) * Q
            #                        for f in frequencies],
            #          color='darkblue', linestyle='--',
            #          label=r'(2) $\tau_{O_2}(\nu) + k_{\rho}(\nu)\cdot Q_i,~ Q_i = '
            #                + '{:.2f}$'.format(Q))
            # plt.plot(frequencies, [model.opacity(brt, self.t_avg) for _, brt in spec],
            #          color='forestgreen', linestyle='-.',
            #          label=r'(3) $\ln(T_{avg}^{\nu}) - \ln(T_{avg}^{\nu} - T_b(\nu))$')
            # w_ = [max(
            #     model.opacity(brt, Tavg=self.t_avg) - model.tauO_theory(f) - model.krho(f) * Q,
            #     0
            # ) / model.kw(f, tcl=self.tcl)
            #       for f, brt in spec]
            # w_max = np.max(w_)
            # w_min = np.min(w_)
            # plt.plot(frequencies, [model.tauO_theory(f) +
            #                        model.krho(f) * Q +
            #                        model.kw(f, self.tcl) * w_min
            #                        for f in frequencies],
            #          color='crimson', linestyle=':',
            #          label=r'(4) $\tau_{O_2}(\nu) + k_{\rho}(\nu)\cdot '
            #                + '{:.2f}'.format(Q) +
            #                r' + k_w(\nu, T_{cl})\cdot W_{\min}$')
            # plt.plot(frequencies, [model.tauO_theory(f) +
            #                        model.krho(f) * Q +
            #                        model.kw(f, self.tcl) * w_max
            #                        for f in frequencies],
            #          color='crimson', linestyle='--',
            #          label=r'(5) $\tau_{O_2}(\nu) + k_{\rho}(\nu)\cdot '
            #                + '{:.2f}'.format(Q) +
            #                r' + k_w(\nu, T_{cl})\cdot W_{\max}$')
            # plt.plot(frequencies, [model.tauO_theory(f) +
            #                        model.krho(f) * Q +
            #                        model.kw(f, self.tcl) * W
            #                        for f in frequencies],
            #          color='crimson', linestyle='-',
            #          label=r'(6) $\tau_{O_2}(\nu) + k_{\rho}(\nu)\cdot '
            #                + '{:.2f}'.format(Q) +
            #                r' + k_w(\nu, T_{cl})\cdot '
            #                + '{:.2f}$'.format(W))
            # leg = plt.legend(loc='best')
            # leg.get_frame().set_linewidth(0.0)

        print('100%   ', flush=True)
        return session_q, session_w

    def dual_frequency(self, freq1: float, freq2: float,
                       t_step: float = None, resolve: bool = False) -> Session:
        s1, s2 = self.m.DATA.get_series(freq1), self.m.DATA.get_series(freq2)
        s1.thin_fast(t_step)
        s2.thin_fast(t_step)

        model = Model(theta=0)

        out = Session()
        for i in range(min(s1.length, s2.length)):
            t1, tb1 = s1.data[i].to_tuple()
            t2, tb2 = s2.data[i].to_tuple()
            t = (t1 + t2) / 2
            T = self.w.Temperature(t, dimension=p.weather.labels.T_C)
            P = self.w.Pressure(t, dimension=p.weather.labels.P_hpa)
            hum = self.w.Rho_abs(t)
            model.setParameters(temperature=T, pressure=P, rho=hum)

            M = np.array([[model.krho(freq1), model.kw(freq1, tcl=self.tcl)],
                          [model.krho(freq2), model.kw(freq2, tcl=self.tcl)]])

            tauE = np.array([model.opacity(tb1, self.t_avg) * math.cos(self.theta),
                             model.opacity(tb2, self.t_avg) * math.cos(self.theta)])

            tauOxygen = np.array([model.tauO_theory(freq1), model.tauO_theory(freq2)])

            q, w = np.linalg.solve(M, tauE - tauOxygen).tolist()

            out.add('q', Point(t, q))
            out.add('w', Point(t, w))

        if resolve:
            w_min = min(out.get_series('w').get_values())

            out = Session()
            for i in range(min(s1.length, s2.length)):
                t1, tb1 = s1.data[i].to_tuple()
                t2, tb2 = s2.data[i].to_tuple()
                t = (t1 + t2) / 2
                T = self.w.Temperature(t, dimension=p.weather.labels.T_C)
                P = self.w.Pressure(t, dimension=p.weather.labels.P_hpa)
                hum = self.w.Rho_abs(t)
                model.setParameters(temperature=T, pressure=P, rho=hum)

                M = np.array([[model.krho(freq1), model.kw(freq1, tcl=self.tcl)],
                              [model.krho(freq2), model.kw(freq2, tcl=self.tcl)]])

                tauE = np.array([model.opacity(tb1, self.t_avg) * math.cos(self.theta),
                                 model.opacity(tb2, self.t_avg) * math.cos(self.theta)])

                tauOxygen = np.array([model.tauO_theory(freq1), model.tauO_theory(freq2)])

                wShift = np.array([model.kw(freq1, tcl=self.tcl) * w_min,
                                   model.kw(freq2, tcl=self.tcl) * w_min])

                q, w = np.linalg.solve(M, tauE - tauOxygen - wShift).tolist()

                out.add('q', Point(t, q))
                out.add('w', Point(t, w))

        return out

    def DualFrequency(self, freq_pairs: list, t_step: float = None) -> Tuple[Session, Session]:
        # ANALYSIS
        # plt.figure(158734)
        # for i, t in enumerate(self.m.DATA.get_timestamps(key=18.0)):
        #     if i > 50:
        #         break
        #     spec = self.m.DATA.get_spectrum(t)
        #     model = Model(theta=0)
        #     T = self.w.Temperature(t, dimension=p.weather.labels.T_C)
        #     P = self.w.Pressure(t, dimension=p.weather.labels.P_hpa)
        #     hum = self.w.Rho_abs(t)
        #     model.setParameters(temperature=T, pressure=P, rho=hum)
        #     freqs, opacity, tau, tau_max, tau_kw = [], [], [], [], []
        #     for freq, brt in spec:
        #         freqs.append(freq)
        #         opacity.append(model.opacity(brt, Tavg=5 + 273))
        #         tau.append(model.tau_theory(freq))
        #         tau_max.append(max(model.tau_theory(freq), model.opacity(brt, Tavg=5 + 273)))
        #
        #     th = model.tau_theory(22.2)
        #     brt = self.m.DATA.get_series(22.2).get(t).val
        #     r = model.opacity(brt, Tavg=5+273)
        #     w = 0.
        #     while th < r:
        #         w += 0.01
        #         th = model.tau_theory(22.2) + model.kw(22.2, tcl=-2) * w
        #     for freq in self.m.DATA.keys:
        #         tau_kw.append(model.tau_theory(freq) + model.kw(freq, -2) * w)
        #
        #     plt.plot(freqs, tau, color="blue")
        #     plt.plot(freqs, opacity, color="green")
        #     plt.plot(freqs, tau_max, color="orange")
        #     plt.plot(freqs, tau_kw, color="crimson")

        q, w = Session(), Session()
        for f1, f2 in freq_pairs:
            s = self.dual_frequency(f1, f2, t_step)
            q.add(Series(key=(f1, f2), data=s.get_series('q').data))
            w.add(Series(key=(f1, f2), data=s.get_series('w').data))
        return q, w
