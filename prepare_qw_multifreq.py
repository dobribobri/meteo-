

import numpy as np
import os
import dill
import sys
import argparse
import time
from termcolor import colored

sys.path.append('../atmrad')
from gpu.atmosphere import Atmosphere, avg
from gpu.weight_funcs import krho
from cpu.core.static.weight_funcs import kw
import gpu.core.math as math


# radiometry_angle = 51.*np.pi/180
radiometry_angle = 0.

frequencies = np.linspace(18.0, 27.2, 47, endpoint=True)

T_cosmic = 2.72548


def createArgParser():
    _p = argparse.ArgumentParser()
    _p.add_argument('-P', '--path_to_dump_dir', default='./dump/summer/2019/',
                    help='Where to get data from?')
    _p.add_argument('-R', '--regularization', default=17.25,
                    help='Regularization coefficient')
    _p.add_argument('--lm', action='store_true', default=False,
                    help='Compute QRETRLM, WRETRLM')
    _p.add_argument('--ms', action='store_true', default=False,
                    help='Compute QRETRMS, WRETRMS')
    _p.add_argument('--tcl', default=0, help="Average effective cloud temperature, Cels.")
    _p.add_argument('--qretrlmname', default='qretrlm_multifreq')
    _p.add_argument('--wretrlmname', default='wretrlm_multifreq')
    _p.add_argument('--qretrmsname', default='qretrms_multifreq')
    _p.add_argument('--wretrmsname', default='wretrms_multifreq')
    return _p


def dump(_obj, _name, _dump_options):
    if not os.path.exists('dump'):
        os.makedirs('dump')
    print(colored('{}...'.format(_name), 'blue'))
    if 'numpy' in _dump_options:
        np.save(os.path.join('dump', '{}.npy'.format(_name)), _obj)
        print(colored('...numpy', 'green'))
    if 'dill' in _dump_options:
        with open(os.path.join('dump', '{}.dump'.format(_name)), 'wb') as _dump:
            dill.dump(_obj, _dump, recurse=True)
        print(colored('...dill', 'green'))


if __name__ == '__main__':

    parser = createArgParser()
    ns = parser.parse_args(sys.argv[1:])
    dump_dir = ns.path_to_dump_dir
    tcl = float(ns.tcl)
    r = float(ns.regularization)
    if not r:
        print(colored('No regularization!\n', 'yellow'))
    else:
        print(colored('Regularization coeff.: {:.3f}\n'.format(r), 'yellow'))

    print(colored('\nDUMP dir is {}'.format(dump_dir), 'blue'))

    TS = np.load(os.path.join(dump_dir, 'ts.npy'))
    # DT = np.load(os.path.join(dump_dir, 'dt.npy'))
    BT = np.load(os.path.join(dump_dir, 'btc1.npy'))
    LM = np.load(os.path.join(dump_dir, 'lm.npy'))
    MS = np.load(os.path.join(dump_dir, 'ms.npy'))
    # ID = np.load(os.path.join(dump_dir, 'id.npy'))

    print('\nРазмерности и типы входных данных')
    print(
        'TS ', TS.shape, TS.dtype, '\n',
        # 'DT ', DT.shape, DT.dtype, '\n',
        # 'ID ', ID.shape, ID.dtype, '\n',
        'BT ', BT.shape, BT.dtype, '\n',
        'LM ', LM.shape, LM.dtype, '\n',
        'MS ', MS.shape, MS.dtype, '\n',
    )

    batch_size = 0
    while batch_size < 1:
        print('\nВведите размер одного батча')
        try:
            batch_size = int(input())
        except Exception as e:
            print(e)
            continue
        if batch_size < 1:
            print('Размер батча не может быть меньше 1')
            continue
    print()

    with open('Dolgoprudnyj_gridded.dump', 'rb') as _dump:
        meteosonde_data = dill.load(_dump)

    # channels = {}
    # for i, f in enumerate(frequencies):
    #     channels[np.round(f, decimals=1)] = i

    print("Средняя эффективная температура облака t_cl = {}".format(tcl))

    K_W_STD = np.asarray([kw(nu, t=tcl) for nu in frequencies])

    _, _, _, alt = meteosonde_data[tuple(MS[0])]

    QSTD, QREAL = np.asarray([]), np.asarray([])
    QRETRLM, WRETRLM = np.asarray([]), np.asarray([])
    QRETRMS, WRETRMS = np.asarray([]), np.asarray([])

    progress = 0.
    n_batches = len(TS) // batch_size

    for n in range(n_batches):
        indexes = list(range(len(TS)))[n * batch_size: n * batch_size + batch_size]

        start = time.time()

        T0, P0, rho0 = [], [], []
        T, P, rho_rel = [], [], []
        for i in indexes:
            T0_, P0_, rho0_, *_ = LM[i]
            T_, P_, rho_rel_, _ = meteosonde_data[tuple(MS[i])]

            T0.append(T0_)
            P0.append(P0_)
            rho0.append(rho0_)

            T.append(T_)
            P.append(P_)
            rho_rel.append(rho_rel_)

        T0, P0, rho0 = np.asarray(T0), np.asarray(P0), np.asarray(rho0)     # (batch_size, )
        stdAtm = Atmosphere.Standard(T0=T0, P0=P0, rho0=rho0, H=15, dh=15. / 1000)
        # данные уже загружены на GPU
        del T0
        del P0
        del rho0
        # Z x batch_size -> batch_size x 1 x Z
        stdAtm.temperature = math.move_axis(math.as_tensor([math.transpose(stdAtm.temperature)]), 0, 1)
        stdAtm.pressure = math.move_axis(math.as_tensor([math.transpose(stdAtm.pressure)]), 0, 1)
        stdAtm.absolute_humidity = math.move_axis(math.as_tensor([math.transpose(stdAtm.absolute_humidity)]), 0, 1)
        stdAtm.liquid_water = math.move_axis(math.as_tensor([math.transpose(stdAtm.liquid_water)]), 0, 1)

        QSTD = np.hstack((QSTD, np.asarray(stdAtm.Q)[:, 0]))

        # batch_size x Z -> batch_size x 1 x Z
        T, P, rho_rel = np.moveaxis(np.asarray([T]), 0, 1), np.moveaxis(np.asarray([P]), 0, 1), \
            np.moveaxis(np.asarray([rho_rel]), 0, 1)
        realAtm = Atmosphere(T, P, RelativeHumidity=rho_rel, altitudes=alt)
        del T
        del P
        del rho_rel

        QREAL = np.hstack((QREAL, np.asarray(realAtm.Q)[:, 0]))

        if not r:

            if int(ns.lm):
                # MULTI FREQ LOCALMETEO
                brt = math.as_tensor([[BT[i, :]] for i in indexes])     # под углом | (batch_size, 1, 47)

                t_avg_down_std = math.as_tensor(
                    [avg.downward.T(stdAtm, nu, radiometry_angle) for nu in frequencies]
                )   # под углом | (47, batch_size, 1)
                t_avg_down_std = math.move_axis(t_avg_down_std, 0, -1)  # (batch_size, 1, 47)

                tau_o_std = math.as_tensor(
                    [stdAtm.opacity.oxygen(nu) for nu in frequencies]
                )   # в зените | (47, batch_size, 1)
                tau_o_std = math.move_axis(tau_o_std, 0, -1)  # (batch_size, 1, 47)

                tau_e_std = math.log(
                    (t_avg_down_std - T_cosmic) / (t_avg_down_std - brt)
                )   # (batch_size, 1, 47) - в зените

                k_rho_std = math.as_tensor(
                    [krho(stdAtm, nu) for nu in frequencies]
                )   # в зените
                k_rho_std = math.move_axis(k_rho_std, 0, -1)  # (batch_size, 1, 47)

                k_w_std = math.move_axis(math.as_tensor([[K_W_STD[:]] * len(indexes)]), 0, 1)  # (batch_size, 1, 47)

                M_std = math.as_tensor([k_rho_std, k_w_std])  # (2, batch_size, 1, 47)
                M_std = math.move_axis(M_std, 0, -1)  # (batch_size, 1, 47, 2)

                right_std = math.move_axis(math.as_tensor([tau_e_std - tau_o_std]), 0, -1)  # (batch_size, 1, 47, 1)

                sol_std = math.linalg_lstsq(M_std, right_std)  # (batch_size, 1, 2, 1)

                QRETRLM = np.hstack((QRETRLM, np.array(sol_std[:, 0, 0, 0])))
                WRETRLM = np.hstack((WRETRLM, np.array(sol_std[:, 0, 1, 0])))

                del brt
                del t_avg_down_std
                del tau_o_std
                del tau_e_std
                del k_rho_std
                del k_w_std
                del M_std
                del right_std
                del sol_std

            if int(ns.ms):
                # MULTI FREQ METEOSONDE
                brt = math.as_tensor([[BT[i, :]] for i in indexes])  # под углом | (batch_size, 1, 47)

                t_avg_down_real = math.as_tensor(
                    [avg.downward.T(realAtm, nu, radiometry_angle) for nu in frequencies]
                )  # под углом | (47, batch_size, 1)
                t_avg_down_real = math.move_axis(t_avg_down_real, 0, -1)  # (batch_size, 1, 47)

                tau_o_real = math.as_tensor(
                    [realAtm.opacity.oxygen(nu) for nu in frequencies]
                )  # в зените | (47, batch_size, 1)
                tau_o_real = math.move_axis(tau_o_real, 0, -1)  # (batch_size, 1, 47)

                tau_e_real = math.log(
                    (t_avg_down_real - T_cosmic) / (t_avg_down_real - brt)
                )  # (batch_size, 1, 47) - в зените

                k_rho_real = math.as_tensor(
                    [krho(realAtm, nu) for nu in frequencies]
                )  # в зените
                k_rho_real = math.move_axis(k_rho_real, 0, -1)  # (batch_size, 1, 47)

                k_w_std = math.move_axis(math.as_tensor([[K_W_STD[:]] * len(indexes)]), 0, 1)  # (batch_size, 1, 47)

                M_real = math.as_tensor([k_rho_real, k_w_std])  # (2, batch_size, 1, 47)
                M_real = math.move_axis(M_real, 0, -1)  # (batch_size, 1, 47, 2)

                right_real = math.move_axis(math.as_tensor([tau_e_real - tau_o_real]), 0, -1)  # (batch_size, 1, 47, 1)

                sol_real = math.linalg_lstsq(M_real, right_real)  # (batch_size, 1, 2, 1)

                QRETRMS = np.hstack((QRETRMS, np.array(sol_real[:, 0, 0, 0])))
                WRETRMS = np.hstack((WRETRMS, np.array(sol_real[:, 0, 1, 0])))

                del brt
                del t_avg_down_real
                del tau_o_real
                del tau_e_real
                del k_rho_real
                del k_w_std
                del M_real
                del right_real
                del sol_real

        else:

            r = math.as_tensor(r)

            if int(ns.lm):
                # MULTI FREQ LOCALMETEO WITH REGULARIZATION
                brt = math.as_tensor([[BT[i, :]] for i in indexes])  # под углом | (batch_size, 1, 47)

                t_avg_down_std = math.as_tensor(
                    [avg.downward.T(stdAtm, nu, radiometry_angle) for nu in frequencies]
                )  # под углом | (47, batch_size, 1)
                t_avg_down_std = math.move_axis(t_avg_down_std, 0, -1)  # (batch_size, 1, 47)

                tau_o_std = math.as_tensor(
                    [stdAtm.opacity.oxygen(nu) for nu in frequencies]
                )  # в зените | (47, batch_size, 1)
                tau_o_std = math.move_axis(tau_o_std, 0, -1)  # (batch_size, 1, 47)

                tau_e_std = math.log(
                    (t_avg_down_std - T_cosmic) / (t_avg_down_std - brt)
                )  # (batch_size, 1, 47) - в зените

                k_rho_std = math.as_tensor(
                    [krho(stdAtm, nu) for nu in frequencies]
                )  # в зените
                k_rho_std = math.move_axis(k_rho_std, 0, -1)  # (batch_size, 1, 47)

                k_w_std = math.move_axis(math.as_tensor([[K_W_STD[:]] * len(indexes)]), 0, 1)  # (batch_size, 1, 47)

                a = math.sum_(tau_e_std * k_w_std, axis=-1) - math.sum_(tau_o_std * k_w_std, axis=-1)  # (batch_size, 1)
                b = math.sum_(k_rho_std * k_w_std, axis=-1) / math.sum_(k_rho_std * k_rho_std, axis=-1)
                c = math.sum_(tau_e_std * k_rho_std, axis=-1) - math.sum_(tau_o_std * k_rho_std, axis=-1)
                d = c / math.sum_(k_rho_std * k_rho_std, axis=-1)  # (batch_size, 1)
                p = math.sum_(k_rho_std * k_w_std, axis=-1)  # (batch_size, 1)
                s = math.sum_(k_w_std * k_w_std, axis=-1)  # (batch_size, 1)

                u = b * p - s   # (batch_size, 1)
                w = (u * math.lambertw(-math.exp((a - b * c) * r / u) * r * r / u) - a * r + b * c * r) / (r * u)
                q = d - b * w   # (batch_size, 1)

                QRETRLM = np.hstack((QRETRLM, np.array(q[:, 0])))
                WRETRLM = np.hstack((WRETRLM, np.array(w[:, 0])))

                del brt
                del t_avg_down_std
                del tau_o_std
                del tau_e_std
                del k_rho_std
                del k_w_std
                del a
                del b
                del c
                del d
                del p
                del s
                del u
                del q
                del w

            if int(ns.ms):
                # MULTI FREQ METEOSONDE WITH REGULARIZATION
                brt = math.as_tensor([[BT[i, :]] for i in indexes])  # под углом | (batch_size, 1, 47)

                t_avg_down_real = math.as_tensor(
                    [avg.downward.T(realAtm, nu, radiometry_angle) for nu in frequencies]
                )  # под углом | (47, batch_size, 1)
                t_avg_down_real = math.move_axis(t_avg_down_real, 0, -1)  # (batch_size, 1, 47)

                tau_o_real = math.as_tensor(
                    [realAtm.opacity.oxygen(nu) for nu in frequencies]
                )  # в зените | (47, batch_size, 1)
                tau_o_real = math.move_axis(tau_o_real, 0, -1)  # (batch_size, 1, 47)

                tau_e_real = math.log(
                    (t_avg_down_real - T_cosmic) / (t_avg_down_real - brt)
                )  # (batch_size, 1, 47) - в зените

                k_rho_real = math.as_tensor(
                    [krho(realAtm, nu) for nu in frequencies]
                )  # в зените
                k_rho_real = math.move_axis(k_rho_real, 0, -1)  # (batch_size, 1, 47)

                k_w_std = math.move_axis(math.as_tensor([[K_W_STD[:]] * len(indexes)]), 0, 1)  # (batch_size, 1, 47)

                a = math.sum_(tau_e_real * k_w_std, axis=-1) - math.sum_(tau_o_real * k_w_std, axis=-1)
                b = math.sum_(k_rho_real * k_w_std, axis=-1) / math.sum_(k_rho_real * k_rho_real, axis=-1)
                c = math.sum_(tau_e_real * k_rho_real, axis=-1) - math.sum_(tau_o_real * k_rho_real, axis=-1)
                d = c / math.sum_(k_rho_real * k_rho_real, axis=-1)  # (batch_size, 1)
                p = math.sum_(k_rho_real * k_w_std, axis=-1)  # (batch_size, 1)
                s = math.sum_(k_w_std * k_w_std, axis=-1)  # (batch_size, 1)

                u = b * p - s  # (batch_size, 1)
                w = (u * math.lambertw(-math.exp((a - b * c) * r / u) * r * r / u) - a * r + b * c * r) / (r * u)
                q = d - b * w  # (batch_size, 1)

                QRETRMS = np.hstack((QRETRMS, np.array(q[:, 0])))
                WRETRMS = np.hstack((WRETRMS, np.array(w[:, 0])))

                del brt
                del t_avg_down_real
                del tau_o_real
                del tau_e_real
                del k_rho_real
                del k_w_std
                del a
                del b
                del c
                del d
                del p
                del s
                del u
                del q
                del w

        del stdAtm
        del realAtm

        # if int(ns.lm):
        #     np.save(os.path.join(dump_dir, '{}'.format(ns.qretrlmname)), QRETRLM)
        #     np.save(os.path.join(dump_dir, '{}'.format(ns.wretrlmname)), WRETRLM)
        # if int(ns.ms):
        #     np.save(os.path.join(dump_dir, '{}'.format(ns.qretrmsname)), QRETRMS)
        #     np.save(os.path.join(dump_dir, '{}'.format(ns.wretrmsname)), WRETRMS)

        progress += len(indexes)
        end = time.time() - start

        print(colored('Total progress: {:.5f}% \t\t Batch no. {} out of {}\t\t Time spent per batch: {:.4f}'.format(
            progress / len(TS) * 100.,
            n + 1, n_batches,
            end),
            'green')
        )

    print('\nСохраняем...')

    QSTD = np.asarray(QSTD)
    QREAL = np.asarray(QREAL)

    # np.save(os.path.join(dump_dir, 'qstd.npy'), QSTD)
    # np.save(os.path.join(dump_dir, 'qreal.npy'), QREAL)

    if int(ns.lm):
        np.save(os.path.join(dump_dir, '{}'.format(ns.qretrlmname)), QRETRLM)
        np.save(os.path.join(dump_dir, '{}'.format(ns.wretrlmname)), WRETRLM)
    if int(ns.ms):
        np.save(os.path.join(dump_dir, '{}'.format(ns.qretrmsname)), QRETRMS)
        np.save(os.path.join(dump_dir, '{}'.format(ns.wretrmsname)), WRETRMS)
