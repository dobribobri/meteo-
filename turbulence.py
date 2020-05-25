
import math
import sys
from collections import defaultdict
from rec_itu_p676_3 import Model
from borland.datetime import TDateTime


def get_avg_weather(WDATA):
    print(WDATA.keys())
    T, P, rho = 0, 0, 0
    for key in WDATA.keys():
        avg = 0
        min, max = sys.maxsize, -sys.maxsize
        for _, v in WDATA[key]:
            avg += v
            if v < min:
                min = v
            if v > max:
                max = v
        avg /= len(WDATA[key])
        if key == 'temper':
            T = avg
        if key == 'mmrtst':
            P = avg * 1.33322
        if key == 'pr_hpa':
            pass
        if key == 'rhoabs':
            rho = avg
        if key == 'v_wind':
            pass
        if key == 'rainrt':
            pass
    return T, P, rho


def c_alpha(SFDATA, WDATA, colm_ob_lim=True):
    T, P, rho = get_avg_weather(WDATA)
    print(T, P, rho)
    model = Model(T, P, rho)
    res = defaultdict(list)
    Tav = 5 + 273   # K
    L = model.H2    # км
    Vw_h = 10          # м/с
    for freq in SFDATA.keys():
        gamma = model.tau_theory(frequency=freq)    # нп
        for tau, val in SFDATA[freq]:
            if tau == 0:
                continue
            if colm_ob_lim and tau >= TDateTime(ss=50).toDouble():
                break
            # print(2.91 * L * (Tav**2) * math.pow(Vw_h, 5/3) * math.exp(-2*gamma) * math.pow(tau, 5/3))
            v = (
                math.sqrt(
                    val**2
                    /
                    (2.91 * L * (Tav**2) * math.pow(Vw_h, 5/3) *
                        math.exp(-2*gamma) * math.pow(tau, 5/3))
                )
            )
            res[freq].append((tau, v))
    return res

