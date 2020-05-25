# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from termcolor import colored
from borland.datetime import TDateTime


def thin_out(data: list, time_step_sec: int):
    if time_step_sec == 0:
        return data[:]
    tB, _ = data[0]
    tE, _ = data[len(data)-1]

    step = TDateTime(ss=time_step_sec).toDouble()

    n = (tE - tB) // step

    jL = 0
    out = []
    # __flag = True
    # err = 0
    for i in range(int(n)):
        time = tB + i * step
        val, k = 0, 0
        for j in range(jL, len(data)):
            t, v = data[j]
            if t > time + step / 2:
                jL = j
                break
            val += v
            k += 1
        if val:
            out.append((time, val / k))
        else:
            # if __flag:
            #     print('')
            #     __flag = False
            # print(colored('Не найдено значений в интервале времени от {} до {} (TDateTime формат)'.format(
            #     time - step / 2, time + step / 2
            # ), 'red'))
            # err += 1
            pass
    return out
