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
        print('100%   ', flush=True)
        return out

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
