# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

import sys
import math
import time
from termcolor import colored
from session import Session, Series, Point
from settings import parameter
# from borland_datetime import TDateTime


def structural_function(tb: Series,
                        t_step: float = None,
                        part: float = 1,
                        rightLimit: float = sys.maxsize) -> Series:
    tb.thin_fast(t_step)

    dt_avg = 0
    for i in range(tb.length - 1):
        dt_avg += (tb.data[i+1].time - tb.data[i].time)
    dt_avg /= (tb.length - 1)

    out = Series(key=tb.key)
    for m in range(int(part * tb.length)):
        if m * dt_avg > rightLimit:
            break
        I = 0.
        for k in range(tb.length - m):
            I += (tb.data[k+m].val - tb.data[k].val) ** 2
        I = math.sqrt(I / (tb.length - m))
        out.add(Point(m * dt_avg, I))
    return out
    

def structural_functions(MDATA: Session,
                         t_step: float = parameter.struct_func.t_step,
                         part: float = parameter.struct_func.part,
                         rightShowLimit: float = parameter.struct_func.rightShowLimit) -> Session:
    print("Structural functions calculation...\t", end='', flush=True)
    start_time = time.time()
    data = Session()
    for freq in MDATA.keys:
        data.add(structural_function(MDATA.get_series(freq), t_step, part, rightShowLimit))
    print('{:.3f} sec\t'.format(time.time() - start_time), end='')
    print('[' + colored('OK', 'green') + ']')
    return data
