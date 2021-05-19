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
import ctypes
import os


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

    def leastSquares(self, frequencies: list = None,
                     t_step: float = None) -> Tuple[Session, Session]:
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
            print('{:.2f}%'.format(j / len(timestamps) * 100), end='\r', flush=True)
            spec = session.get_spectrum(t)
            T = self.w.Temperature(t, dimension=p.weather.labels.T_C)
            P = self.w.Pressure(t, dimension=p.weather.labels.P_hpa)
            hum = self.w.Rho_abs(t)
            model.setParameters(temperature=T, pressure=P, rho=hum)
            A = np.zeros((2, 2), dtype=float)
            b = np.zeros(2, dtype=float)
            for f, brt in spec:
                krho, kw = model.krho(f), model.kw(f, self.tcl)
                A += np.array([[krho * krho, krho * kw], [krho * kw, kw * kw]])
                b_ = model.opacity(brt, self.t_avg) * math.cos(self.theta) - model.tauO_theory(f)
                b += np.array([b_ * krho, b_ * kw])
            q, w = np.linalg.solve(A, b).tolist()
            session_q.add('q', Point(t, q))
            session_w.add('w', Point(t, w))
        return session_q, session_w

    def optimize(self, frequencies: list = None,
                 t_step: float = None) -> Tuple[Session, Session]:
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
            print('{:.2f}%'.format(j / len(timestamps) * 100), end='\r', flush=True)
            spec = session.get_spectrum(t)
            T = self.w.Temperature(t, dimension=p.weather.labels.T_C)
            P = self.w.Pressure(t, dimension=p.weather.labels.P_hpa)
            hum = self.w.Rho_abs(t)
            model.setParameters(temperature=T, pressure=P, rho=hum)
            A = np.zeros((2, 2), dtype=float)
            b = np.zeros(2, dtype=float)
            for f, brt in spec:
                krho, kw = model.krho(f), model.kw(f, self.tcl)
                A += np.array([[krho * krho, krho * kw], [krho * kw, kw * kw]])
                b_ = model.opacity(brt, self.t_avg) * math.cos(self.theta) - model.tauO_theory(f)
                b += np.array([b_ * krho, b_ * kw])
            q, w = np.linalg.solve(A, b).tolist()
            session_q.add('q', Point(t, q))
            session_w.add('w', Point(t, w))
        mval = min(session_w.get_series('w').data, key=lambda p_: p_.val)  # TBD
        if mval.val < 0:
            session_q = Session()
            session_w.get_series('w').data = [Point(p_.time, p_.val - mval.val)
                                              for p_ in session_w.get_series('w').data]  # TBD
            for j, t in enumerate(timestamps):
                print('{:.2f}%'.format(j / len(timestamps) * 100), end='\r', flush=True)
                spec = session.get_spectrum(t)
                T = self.w.Temperature(t, dimension=p.weather.labels.T_C)
                P = self.w.Pressure(t, dimension=p.weather.labels.P_hpa)
                hum = self.w.Rho_abs(t)
                model.setParameters(temperature=T, pressure=P, rho=hum)
                a, b = 0., 0.
                for f, brt in spec:
                    krho, kw = model.krho(f), model.kw(f, self.tcl)
                    a += krho * (model.opacity(brt, self.t_avg) * math.cos(self.theta) -  # TBD
                                 model.tauO_theory(f) - kw * session_w.get_series('w').data[j].val)
                    b += krho * krho
                q = a / b
                session_q.add('q', Point(t, q))
        return session_q, session_w

    def DUALFREQCPP(self, freq_pairs=None, t_step: float = None) -> Tuple[Session, Session]:
        if freq_pairs is None:
            freq_pairs = p.freqs.qw2_freq_pairs

        class mcps_t(ctypes.Structure):
            _fields_ = [('Q', ctypes.c_double), ('W', ctypes.c_double)]

        # domainpp = ctypes.CDLL('/home/dobri/QtProjects/SMAC/SMAC/libdomainpp.so', mode=os.RTLD_LAZY)
        domainpp = ctypes.CDLL('libdomainpp.so', mode=os.RTLD_LAZY)
        domainpp.domain_new.argtypes = [ctypes.c_double, ctypes.c_double]
        domainpp.domain_new.restype = ctypes.c_void_p

        domainpp.get_qw.argtypes = [ctypes.c_void_p,
                                    ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double,
                                    ctypes.c_double,
                                    ctypes.c_double, ctypes.c_double, ctypes.c_double]
        domainpp.get_qw.restype = ctypes.POINTER(mcps_t)

        domain = domainpp.domain_new(ctypes.c_double(self.t_avg), ctypes.c_double(self.tcl))

        q, w = Session(), Session()
        for f1, f2 in freq_pairs:
            s1, s2 = self.m.DATA.get_series(f1), self.m.DATA.get_series(f2)
            s1.thin_fast(t_step)
            s2.thin_fast(t_step)
            s = Session()
            for i in range(min(s1.length, s2.length)):
                t1, tb1 = s1.data[i].to_tuple()
                t2, tb2 = s2.data[i].to_tuple()
                t = (t1 + t2) / 2
                T = self.w.Temperature(t, dimension=p.weather.labels.T_C)
                P = self.w.Pressure(t, dimension=p.weather.labels.P_hpa)
                hum = self.w.Rho_abs(t)

                ret = domainpp.get_qw(domain, ctypes.c_double(f1), ctypes.c_double(f2),
                                      ctypes.c_double(tb1), ctypes.c_double(tb2),
                                      ctypes.c_double(self.theta),
                                      ctypes.c_double(T), ctypes.c_double(P), ctypes.c_double(hum))

                s.add('q', Point(t, ret.contents.Q))
                s.add('w', Point(t, ret.contents.W))

            q.add(Series(key=(f1, f2), data=s.get_series('q').data))
            w.add(Series(key=(f1, f2), data=s.get_series('w').data))
        return q, w

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
        q, w = Session(), Session()
        for f1, f2 in freq_pairs:
            s = self.dual_frequency(f1, f2, t_step)
            q.add(Series(key=(f1, f2), data=s.get_series('q').data))
            w.add(Series(key=(f1, f2), data=s.get_series('w').data))
        return q, w
