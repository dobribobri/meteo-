# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from session import Series, Point


class Eliminate:

    @staticmethod
    def __median(s):
        m = s[len(s) // 2]
        if len(s) % 2 == 0:
            m = (s[len(s) // 2] + s[len(s) // 2 - 1]) / 2
        return m

    @staticmethod
    def time_series(s: Series) -> Series:
        q1 = Eliminate.__median([s.data[i].val for i in range(0, len(s.data) // 2)])
        q3 = Eliminate.__median([s.data[i].val for i in range(len(s.data) // 2, len(s.data))])
        shift = (q3 - q1) * 3
        l_lim = q1 - shift
        r_lim = q3 + shift
        n = Series(s.key)
        for t, v in s.data:
            if l_lim < v < r_lim:
                n.add(Point(t, v))
        return n
