# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from typing import Iterable
from pythonlangutil.overload import Overload, signature
from collections import defaultdict
# import inspect
# import types


# class MultiMethod:
#     """
#     Represents a single multimethod.
#     """
#     def __init__(self, name):
#         self._methods = {}
#         self.__name__ = name
#
#     def register(self, meth):
#         """
#         Register a new method as a multimethod
#         """
#         sig = inspect.signature(meth)
#
#         # Build a type signature from the method's annotations
#         types = []
#         for name, parm in sig.parameters.items():
#             if name == 'self':
#                 continue
#             if parm.annotation is inspect.Parameter.empty:
#                 raise TypeError(
#                     'Argument {} must be annotated with a type'.format(name)
#                 )
#             if not isinstance(parm.annotation, type):
#                 raise TypeError(
#                     'Argument {} annotation must be a type'.format(name)
#                 )
#             if parm.default is not inspect.Parameter.empty:
#                 self._methods[tuple(types)] = meth
#             types.append(parm.annotation)
#
#         self._methods[tuple(types)] = meth
#
#     def __call__(self, *args):
#         """
#         Call a method based on type signature of the arguments
#         """
#         types = tuple(type(arg) for arg in args[1:])
#         meth = self._methods.get(types, None)
#         if meth:
#             return meth(*args)
#         else:
#             raise TypeError('No matching method for types {}'.format(types))
#
#     def __get__(self, instance, cls):
#         """
#         Descriptor method needed to make calls work in a class
#         """
#         if instance is not None:
#             return types.MethodType(self, instance)
#         else:
#             return self
#
#
# class MultiDict(dict):
#     """
#     Special dictionary to build multimethods in a metaclass
#     """
#     def __setitem__(self, key, value):
#         if key in self:
#             # If key already exists, it must be a multimethod or callable
#             current_value = self[key]
#             if isinstance(current_value, MultiMethod):
#                 current_value.register(value)
#             else:
#                 mvalue = MultiMethod(key)
#                 mvalue.register(current_value)
#                 mvalue.register(value)
#                 super().__setitem__(key, mvalue)
#         else:
#             super().__setitem__(key, value)
#
#
# class MultipleMeta(type):
#     """
#     Metaclass that allows multiple dispatch of methods
#     """
#     def __new__(cls, clsname, bases, clsdict):
#         return type.__new__(cls, clsname, bases, dict(clsdict))
#
#     @classmethod
#     def __prepare__(cls, clsname, bases):
#         return MultiDict()


class Point:
    def __init__(self, time: float = None, val: float = None):
        self.time = time
        self.val = val

    def merge(self, point: 'Point'):
        self.time = (self.time + point.time) / 2
        self.val = (self.val + point.val) / 2


class Series:
    def __init__(self, frequency: float = None, data: Iterable[Point] = None):
        self.freq = frequency
        if data:
            self.data = list(data)
        else:
            self.data = []

    @property
    def is_empty(self):
        if self.data:
            return False
        return True

    @property
    def length(self):
        return len(self.data)

    def add(self, *points):
        for p in points:
            self.data.append(p)

    def get_values(self):
        return [p.val for p in self.data]

    def get_timestamps(self):
        return [p.time for p in self.data]

    def rm_t_zeros(self):
        self.data = [p for p in self.data if p.time != 0]

    def rm_v_zeros(self):
        self.data = [p for p in self.data if p.val != 0]

    def remove_zeros(self, timeQ=True, valQ=True):
        if timeQ:
            self.rm_t_zeros()
        if valQ:
            self.rm_v_zeros()

    def sort(self):
        self.data = sorted(self.data, key=lambda point: point.time)

    @property
    def t_start(self):
        return min(self.get_timestamps())

    @property
    def t_stop(self):
        return max(self.get_timestamps())

    def get_time_bounds(self):
        return self.t_start, self.t_stop

    def apply_to_points(self, func):
        self.data = [func(p) for p in self.data]

    def apply_to_data(self, func):
        self.data = func(self.data)

    def set_upper_threshold(self, threshold: float):
        self.data = [p for p in self.data if p.val <= threshold]

    def cut(self, t_start: float, t_stop: float):
        self.data = [p for p in self.data if t_start <= p.time <= t_stop]


class Session:
    def __init__(self, series: Iterable[Series] = None):
        if series:
            self.series = list(series)
        else:
            self.series = []

    @property
    def freqs(self):
        freqs = []
        for s in self.series:
            freqs.append(s.freq)
        return freqs

    @property
    def series_count(self):
        return len(self.series)

    def get_series_pos(self, frequency: float):
        for i in range(self.series_count):
            if self.series[i].freq == frequency:
                return i
        return None

    @Overload
    @signature('Series')
    def add(self, s: Series):
        i = self.get_series_pos(s.freq)
        if i:
            self.series[i].add(*s.data)
            return
        self.series.append(s)

    @add.overload
    @signature('float', 'Point')
    def add(self, frequency: float, point: Point):
        i = self.get_series_pos(frequency)
        if i:
            self.series[i].add(point)
            return
        s = Series(frequency)
        s.add(point)
        self.series.append(s)

    @add.overload
    @signature('float', 'list')
    def add(self, frequency: float, data: list):
        self.add(Series(frequency, data))

    def get_series(self, frequency: float):
        for s in self.series:
            if s.freq == frequency:
                return s
        return Series()

    def get_values(self, frequency: float):
        return self.get_series(frequency).get_values()

    def get_timestamps(self, frequency: float):
        return self.get_series(frequency).get_timestamps()

    @Overload
    @signature('float', 'list')
    def replace(self, frequency: float, data: list):
        i = self.get_series_pos(frequency)
        if i:
            self.series[i].data = data
            return
        self.add(Series(frequency, data))

    @replace.overload
    @signature('Series')
    def replace(self, s: Series):
        self.replace(s.freq, s.data)

    def sort(self):
        self.series = sorted(self.series, key=lambda s: s.freq)

    def remove_zeros(self, timeQ=True, valQ=True):
        for i in range(self.series_count):
            self.series[i].remove_zeros(timeQ, valQ)

    def time_sorting(self):
        for i in range(self.series_count):
            self.series[i].sort()

    def to_defaultdict(self):
        d = defaultdict(list)
        for s in self.series:
            for p in s.data:
                d[s.freq].append((p.time, p.val))
        return d

    @property
    def t_inf(self):
        return max([s.t_start for s in self.series])

    @property
    def t_sup(self):
        return min([s.t_stop for s in self.series])

    def get_time_bounds(self):
        return self.t_inf, self.t_sup

    def apply_to_series(self, func):
        for i in range(self.series_count):
            self.series[i] = func(self.series[i])

    def set_upper_threshold(self, threshold: float):
        for i in range(self.series_count):
            self.series[i].set_upper_threshold(threshold)

    def cut(self, t_start: float, t_stop: float):
        for i in range(self.series_count):
            self.series[i].cut(t_start, t_stop)
