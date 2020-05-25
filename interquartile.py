# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#


class Eliminate:

    @staticmethod
    def __median(s):
        m = s[len(s) // 2]
        if len(s) % 2 == 0:
            m = (s[len(s) // 2] + s[len(s) // 2 - 1]) / 2
        return m

    @staticmethod
    def time_series(data: list, threshold_percentage: float = None):
        s = []
        for _, v in data:
            s.append(v)
        s = sorted(s)
        q2 = Eliminate.__median(s)
        q1 = Eliminate.__median([s[i] for i in range(0, len(s) // 2)])
        q3 = Eliminate.__median([s[i] for i in range(len(s) // 2, len(s))])
        shift = (q3 - q1) * 3
        l_lim = q1 - shift
        r_lim = q3 + shift
        ndata = []
        for t, v in data:
            if l_lim < v < r_lim:
                ndata.append((t, v))
        if threshold_percentage:
            m = Eliminate.__median([e for e in s if l_lim < e < r_lim])
            p = q2 / m * 100 - 100
            if p >= threshold_percentage:
                return ndata
            else:
                return data
        return ndata
