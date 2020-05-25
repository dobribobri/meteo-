# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from collections import defaultdict
import math
from thinner import thin_out
import time
from termcolor import colored
from measurement import Measurement
from default import parameter


def structural_function(tbdata: list, thinning: int = 11, part: float = 1 / 20):
    data = thin_out(tbdata, thinning)

    nsize = len(data)

    dt_avg = 0
    for i in range(nsize - 1):
        t0, _ = data[i]
        t1, _ = data[i+1]
        dt_avg += (t1 - t0)
    dt_avg /= (nsize - 1)

    out = []
    for m in range(int(part * nsize)):
        Em = 0.
        for k in range(nsize - m):
            _, x1 = data[k + m]
            _, x0 = data[k]
            Em += (x1 - x0)**2
        Em = math.sqrt(Em / (nsize - m))
        if m * dt_avg < parameter.struct_func.rightShowLimit:
            out.append((m * dt_avg, Em))

    return out
    

def structural_functions(m: Measurement, thinning: int = 11, part: float = 1 / 20):
    print("Расчёт структурных функций...\t", end='', flush=True)
    start_time = time.time()
    data = defaultdict(list)
    tbdata = []
    for freq in m.DATA.keys():
        data[freq] = structural_function(m.DATA[freq], thinning, part)
    print('{:.3f} sec\t'.format(time.time() - start_time), end='')
    print('[' + colored('OK', 'green') + ']')
    return data
