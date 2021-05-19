# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from typing import Iterable, Tuple, Any
from pythonlangutil.overload import Overload, signature
import sys


class Point:
    def __init__(self, time: Any = None, val: Any = None):
        self.time = time
        self.val = val

    def merge(self, point: 'Point') -> None:
        self.time = (self.time + point.time) / 2
        self.val = (self.val + point.val) / 2

    def to_tuple(self) -> tuple:
        return self.time, self.val

    def to_list(self) -> list:
        return [*self.to_tuple()]


class Series:
    def __init__(self, key: Any = None, data: Iterable[Point] = None):
        self.key = key
        if data:
            self.data = list(data)
        else:
            self.data = []

    @property
    def is_empty(self) -> bool:
        if self.data:
            return False
        return True

    @property
    def length(self) -> int:
        return len(self.data)

    def add(self, *points) -> None:
        for p in points:
            self.data.append(p)

    def get_values(self) -> list:
        return [p.val for p in self.data]

    def get_timestamps(self) -> list:
        return [p.time for p in self.data]

    def get_index_closest_to(self, timestamp: float) -> int:
        md, index = sys.maxsize, 0
        for i, t in sorted(enumerate(self.get_timestamps()), key=lambda item: item[1]):
            d = abs(t - timestamp)
            if d < md:
                md, index = d, i
            else:
                break
        return index

    def get(self, timestamp: float) -> Any:
        return self.data[self.get_index_closest_to(timestamp)]

    def rm_t_zeros(self) -> None:
        self.data = [p for p in self.data if p.time != 0]

    def rm_v_zeros(self) -> None:
        self.data = [p for p in self.data if p.val != 0]

    def remove_zeros(self, timeQ=True, valQ=True) -> None:
        if timeQ:
            self.rm_t_zeros()
        if valQ:
            self.rm_v_zeros()

    def sort_t(self) -> None:
        self.data = sorted(self.data, key=lambda point: point.time)

    @property
    def t_start(self) -> float:
        return min(self.get_timestamps())

    @property
    def t_stop(self) -> float:
        return max(self.get_timestamps())

    def get_time_bounds(self) -> Tuple[float, float]:
        return self.t_start, self.t_stop

    def apply_to_points(self, func) -> None:
        self.data = [func(p) for p in self.data]

    def apply_to_data(self, func) -> None:
        self.data = func(self.data)

    def set_upper_threshold(self, threshold: float) -> None:
        self.data = [p for p in self.data if p.val <= threshold]

    def cut(self, t_start: float, t_stop: float) -> None:
        self.data = [p for p in self.data if t_start <= p.time <= t_stop]

    def thin(self, t_step: float) -> None:
        if t_step:
            t, t_stop = self.get_time_bounds()
            data = []
            while t < t_stop:
                data.append(self.get(t))
                t += t_step
            self.data = data

    def thin_fast(self, t_step: float) -> None:
        if t_step:
            t_start, t_stop = self.get_time_bounds()
            n = (t_stop - t_start) // t_step
            jL, data = 0, []
            for i in range(int(n)):
                time = t_start + i * t_step
                val, k = 0, 0
                for j in range(jL, len(self.data)):
                    t, v = self.data[j].to_tuple()
                    if t > time + t_step / 2:
                        jL = j
                        break
                    val += v
                    k += 1
                if val:
                    data.append(Point(time, val / k))
                else:
                    pass
            self.data = data

    def __len__(self):
        return self.length

    def __str__(self):
        if self.length > 3:
            return '{}: {:.2f}, {}: {:.2f}, ..., {}: {:.2f} (total: {})\n'.format(
                *self.data[0].to_tuple(), *self.data[1].to_tuple(), *self.data[-1].to_tuple(),
                self.length
            )
        s = ''
        for p in self.data:
            s += '{}: {:.2f}\n'.format(*p.to_tuple())
        return s


class Session:
    def __init__(self, series: Iterable[Series] = None):
        if series:
            self.series = list(series)
        else:
            self.series = []

    @property
    def keys(self) -> list:
        keys = []
        for s in self.series:
            keys.append(s.key)
        return keys

    @property
    def series_count(self) -> int:
        return len(self.series)

    def get_series_pos(self, key: Any) -> int:
        for i in range(self.series_count):
            if self.series[i].key == key:
                return i
        return -1

    @Overload
    @signature('Series')
    def add(self, s: Series) -> None:
        i = self.get_series_pos(s.key)
        if i != -1:
            self.series[i].add(*s.data)
            return
        self.series.append(s)

    def __add_point_on_key(self, key: Any, point: Point) -> None:
        i = self.get_series_pos(key)
        if i != -1:
            self.series[i].add(point)
            return
        s = Series(key)
        s.add(point)
        self.series.append(s)

    @add.overload
    @signature('float', 'Point')
    def add(self, key: float, point: Point) -> None:
        self.__add_point_on_key(key, point)

    @add.overload
    @signature('str', 'Point')
    def add(self, key: str, point: Point) -> None:
        self.__add_point_on_key(key, point)

    def get_series(self, key: Any) -> Series:
        for s in self.series:
            if s.key == key:
                return s
        return Series()

    def get_values(self, key: Any) -> list:
        return self.get_series(key).get_values()

    def get_timestamps(self, key: Any) -> list:
        return self.get_series(key).get_timestamps()

    def get_timestamps_averaged(self) -> list:
        mlen = self.min_len
        timestamps = [0] * mlen
        for s in self.series:
            ts = sorted(s.get_timestamps())
            timestamps = [timestamps[i] + ts[i] for i in range(mlen)]
        return [timestamps[i] / len(self.series) for i in range(mlen)]

    def get_spectrum(self, timestamp: float) -> list:
        spectrum = []
        for s in self.series:
            spectrum.append((s.key, s.get(timestamp).val))
        return spectrum

    def __replace(self, key: Any, data: list) -> None:
        i = self.get_series_pos(key)
        if i != -1:
            self.series[i].data = data
            return
        self.add(Series(key, data))

    @Overload
    @signature('float', 'list')
    def replace(self, key: float, data: list) -> None:
        self.__replace(key, data)

    @replace.overload
    @signature('str', 'list')
    def replace(self, key: str, data: list) -> None:
        self.__replace(key, data)

    @replace.overload
    @signature('Series')
    def replace(self, s: Series) -> None:
        self.__replace(s.key, s.data)

    def sort(self) -> None:
        self.series = sorted(self.series, key=lambda s: s.key)

    def remove_zeros(self, timeQ=True, valQ=True) -> None:
        for i in range(self.series_count):
            self.series[i].remove_zeros(timeQ, valQ)

    def time_sorting(self) -> None:
        for i in range(self.series_count):
            self.series[i].sort_t()

    def to_dict(self) -> dict:
        d = {}
        for s in self.series:
            for p in s.data:
                d[s.key].append((p.time, p.val))
        return d

    @property
    def t_start(self) -> float:
        return min([s.t_start for s in self.series])

    @property
    def t_stop(self) -> float:
        return max([s.t_stop for s in self.series])

    @property
    def t_inf(self) -> float:
        return max([s.t_start for s in self.series])

    @property
    def t_sup(self) -> float:
        return min([s.t_stop for s in self.series])

    def get_time_bounds(self) -> Tuple[float, float]:
        return self.t_inf, self.t_sup

    def apply_to_series(self, func) -> None:
        for i in range(self.series_count):
            self.series[i] = func(self.series[i])

    def set_upper_threshold(self, threshold: float) -> None:
        for i in range(self.series_count):
            self.series[i].set_upper_threshold(threshold)

    def cut(self, t_start: float, t_stop: float) -> None:
        for i in range(self.series_count):
            self.series[i].cut(t_start, t_stop)

    def thin(self, t_step: float) -> None:
        for s in self.series:
            s.thin(t_step)

    def thin_fast(self, t_step: float) -> None:
        for s in self.series:
            s.thin_fast(t_step)

    @property
    def min_len(self) -> int:
        return min([s.length for s in self.series])

    @property
    def max_len(self) -> int:
        return max([s.length for s in self.series])

    @property
    def avg_len(self) -> int:
        return sum([s.length for s in self.series]) / len(self.series)

    def box(self) -> None:
        self.cut(*self.get_time_bounds())

    def select(self, keys: list) -> 'Session':
        out = Session()
        for key in keys:
            if key not in self.keys:
                raise KeyError
            out.add(self.get_series(key))
        return out

    def copy(self) -> 'Session':
        return self.select(self.keys)

    def __str__(self):
        s = ''
        for series in self.series:
            s += '\n---- {} ----\n'.format(series.key)
            s += series.__str__()
        return s

    def transpose(self):
        boxed = self.copy()
        boxed.box()
        timestamps = boxed.get_timestamps_averaged()
        out = Session()
        for t in timestamps:
            for series in boxed.series:
                out.add(t, Point(series.key, series.get(t).val))
        return out
