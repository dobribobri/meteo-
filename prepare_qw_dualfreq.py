
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

resonance_frequency = 22.2
second_frequencies = [18, 27.2]

T_cosmic = 2.72548


def createArgParser():
    p = argparse.ArgumentParser()
    p.add_argument('-P', '--path_to_dump_dir', default='./dump/summer/2019/',
                   help='Where to get data from?')
    p.add_argument('--tcl', default=0, help="Average effective cloud temperature, Cels.")
    p.add_argument('--qretrlmname', default='qretrlm')
    p.add_argument('--wretrlmname', default='wretrlm')
    p.add_argument('--qretrmsname', default='qretrms')
    p.add_argument('--wretrmsname', default='wretrms')
    return p


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

    print(colored('\nDUMP dir is {}'.format(dump_dir), 'blue'))

    TS = np.load(os.path.join(dump_dir, 'ts.npy'))
    DT = np.load(os.path.join(dump_dir, 'dt.npy'))
    # BT = np.load(os.path.join(dump_dir, 'bt.npy'))
    BT = np.load(os.path.join(dump_dir, 'btc1.npy'))
    LM = np.load(os.path.join(dump_dir, 'lm.npy'))
    MS = np.load(os.path.join(dump_dir, 'ms.npy'))
    ID = np.load(os.path.join(dump_dir, 'id.npy'))

    print('\nРазмерности и типы входных данных')
    print(
        'TS ', TS.shape, TS.dtype, '\n',
        'DT ', DT.shape, DT.dtype, '\n',
        'ID ', ID.shape, ID.dtype, '\n',
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

    channels = {}
    for i, f in enumerate(np.linspace(18, 27.2, 47, endpoint=True)):
        channels[np.round(f, decimals=1)] = i

    # frequencies = [resonance_channel] + second_channel
    frequency_pairs = [(resonance_frequency, sc) for sc in second_frequencies]

    print("Средняя эффективная температура облака t_cl = {}".format(tcl))

    K_W_STD = [[kw(nu, t=tcl) for nu in freq_pair] for freq_pair in frequency_pairs]

    _, _, _, alt = meteosonde_data[tuple(MS[0])]

    QSTD, QREAL = np.asarray([]), np.asarray([])
    QRETRLM, WRETRLM = np.asarray([[]] * len(frequency_pairs)), np.asarray([[]] * len(frequency_pairs))
    QRETRMS, WRETRMS = np.asarray([[]] * len(frequency_pairs)), np.asarray([[]] * len(frequency_pairs))

    progress = 0.
    n_batches = len(TS) // batch_size
    batches = np.array_split(list(range(len(TS))), n_batches)
    for n, indexes in enumerate(batches):

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

        resonance = dict()
        resonance['tb_measured'] = np.asarray([[BT[i, :][channels[resonance_frequency]]] for i in indexes])  # под углом
        resonance['t_avg_down_std'] = avg.downward.T(stdAtm, resonance_frequency, radiometry_angle)  # под углом
        resonance['t_avg_down_real'] = avg.downward.T(realAtm, resonance_frequency, radiometry_angle)  # под углом
        resonance['k_rho_std'] = krho(stdAtm, resonance_frequency)  # в зените
        resonance['k_rho_real'] = krho(realAtm, resonance_frequency)  # в зените
        resonance['tau_o_std'] = stdAtm.opacity.oxygen(resonance_frequency)  # в зените
        resonance['tau_o_real'] = realAtm.opacity.oxygen(resonance_frequency)  # в зените

        # LOCALMETEO
        qretrlm, wretrlm = [], []
        for j, (_, nu) in enumerate(frequency_pairs):

            brt = math.as_tensor([
                resonance['tb_measured'],
                np.asarray([[BT[i, :][channels[nu]]] for i in indexes])
            ])
            brt = math.move_axis(brt, 0, -1)    # frequency channels last
            # print('brt ', brt.shape)  # (batch_size, 1, 2)

            t_avg_down_std = math.as_tensor([
                resonance['t_avg_down_std'],
                avg.downward.T(stdAtm, nu, radiometry_angle)
            ])
            t_avg_down_std = math.move_axis(t_avg_down_std, 0, -1)
            # print('t_avg_down_std ', t_avg_down_std.shape)   # (batch_size, 1, 2)

            k_rho_std = math.as_tensor([
                resonance['k_rho_std'],
                krho(stdAtm, nu)
            ])
            k_rho_std = math.move_axis(k_rho_std, 0, -1)
            # print('k_rho_std ', k_rho_std.shape)    # (batch_size, 1, 2)

            k_w_std = math.move_axis(math.as_tensor([[K_W_STD[j]] * len(indexes)]), 0, 1)
            # print('k_w_std ', k_w_std.shape)    # (batch_size, 1, 2)

            M_std = math.move_axis(math.as_tensor([k_rho_std, k_w_std]), 0, -1)
            # print('M_std ', M_std.shape)    # (batch_size, 1, 2, 2)

            tau_o_std = math.as_tensor([
                resonance['tau_o_std'],
                stdAtm.opacity.oxygen(nu)
            ])
            tau_o_std = math.move_axis(tau_o_std, 0, -1)
            # print('tau_o_std ', tau_o_std.shape)    # (batch_size, 1, 2)

            tau_e_std = math.log(
                (t_avg_down_std - T_cosmic) / (t_avg_down_std - brt)
            )
            # print('tau_e_std ', tau_e_std.shape)    # (batch_size, 1, 2)

            right_std = math.move_axis(math.as_tensor([tau_e_std - tau_o_std]), 0, -1)
            # print('right_std ', right_std.shape)    # (batch_size, 1, 2, 1)

            sol_std = math.linalg_solve(M_std, right_std)
            # print('sol_std ', sol_std.shape)    # (batch_size, 1, 2, 1)

            qretrlm.append(np.array(sol_std[:, 0, 0, 0]))
            wretrlm.append(np.array(sol_std[:, 0, 1, 0]))

        del brt
        del t_avg_down_std
        del k_rho_std
        del k_w_std
        del M_std
        del tau_o_std
        del tau_e_std
        del right_std
        del sol_std

        # METEOSONDE
        qretrms, wretrms = [], []
        for j, (_, nu) in enumerate(frequency_pairs):

            brt = math.as_tensor([
                resonance['tb_measured'],
                np.asarray([[BT[i, :][channels[nu]]] for i in indexes])
            ])
            brt = math.move_axis(brt, 0, -1)

            t_avg_down_real = math.as_tensor([
                resonance['t_avg_down_real'],
                avg.downward.T(realAtm, nu, radiometry_angle)
            ])
            t_avg_down_real = math.move_axis(t_avg_down_real, 0, -1)

            k_rho_real = math.as_tensor([
                resonance['k_rho_real'],
                krho(realAtm, nu)
            ])
            k_rho_real = math.move_axis(k_rho_real, 0, -1)

            k_w_std = math.move_axis(math.as_tensor([[K_W_STD[j]] * len(indexes)]), 0, 1)

            M_real = math.move_axis(math.as_tensor([k_rho_real, k_w_std]), 0, -1)

            tau_o_real = math.as_tensor([
                resonance['tau_o_real'],
                realAtm.opacity.oxygen(nu)
            ])
            tau_o_real = math.move_axis(tau_o_real, 0, -1)

            tau_e_real = math.log(
                (t_avg_down_real - T_cosmic) / (t_avg_down_real - brt)
            )

            right_real = math.move_axis(math.as_tensor([tau_e_real - tau_o_real]), 0, -1)

            sol_real = math.linalg_solve(M_real, right_real)

            qretrms.append(np.array(sol_real[:, 0, 0, 0]))
            wretrms.append(np.array(sol_real[:, 0, 1, 0]))

        del brt
        del t_avg_down_real
        del k_rho_real
        del k_w_std
        del M_real
        del tau_o_real
        del tau_e_real
        del right_real
        del sol_real

        del resonance

        del stdAtm
        del realAtm

        QRETRLM = np.hstack((QRETRLM, np.asarray(qretrlm)))
        WRETRLM = np.hstack((WRETRLM, np.asarray(wretrlm)))
        QRETRMS = np.hstack((QRETRMS, np.asarray(qretrms)))
        WRETRMS = np.hstack((WRETRMS, np.asarray(wretrms)))

        del qretrlm
        del wretrlm
        del qretrms
        del wretrms

        progress += len(indexes)
        end = time.time() - start

        print(colored('Total progress: {:.5f}% \t\t Batch no. {} out of {}\t\t Time spent per batch: {:.4f}'.format(
            progress / len(TS) * 100.,
            n + 1, len(batches),
            end),
            'green')
        )

    print('\nСохраняем...')

    QSTD = np.asarray(QSTD)
    QREAL = np.asarray(QREAL)

    np.save(os.path.join(dump_dir, 'qstd.npy'), QSTD)
    np.save(os.path.join(dump_dir, 'qreal.npy'), QREAL)
    np.save(os.path.join(dump_dir, '{}.npy'.format(ns.qretrlmname)), QRETRLM)
    np.save(os.path.join(dump_dir, '{}.npy'.format(ns.wretrlmname)), WRETRLM)
    np.save(os.path.join(dump_dir, '{}.npy'.format(ns.qretrmsname)), QRETRMS)
    np.save(os.path.join(dump_dir, '{}.npy'.format(ns.wretrmsname)), WRETRMS)
