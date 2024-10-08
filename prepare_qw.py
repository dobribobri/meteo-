
import numpy as np
import os
import dill
import sys
import argparse
import time
from termcolor import colored

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

sys.path.append('../atmrad')
from cpu.atmosphere import Atmosphere, avg
from cpu.weight_funcs import krho
from cpu.core.static.weight_funcs import kw
import cpu.core.math as math

from multiprocessing import Pool
import tqdm


radiometry_angle = 0.

frequencies = np.linspace(18.0, 27.2, 47, endpoint=True)

T_cosmic = 2.72548


def createArgParser():
    _p = argparse.ArgumentParser()
    _p.add_argument('-P', '--path_to_dump_dir', default='./dump/summer/2019/',
                    help='Where to get data from?')
    _p.add_argument('--nworkers', default=8,
                    help='number of parallel processing kernels')
    _p.add_argument('--lm', action='store_true', default=False,
                    help='Compute QRETRLM, WRETRLM')
    _p.add_argument('--ms', action='store_true', default=False,
                    help='Compute QRETRMS, WRETRMS')
    _p.add_argument('--correction', action='store_true', default=False,
                    help='Correction of the retrieved values')
    _p.add_argument('--tcl', default=0, help="Average effective cloud temperature, Cels.")
    _p.add_argument('--qstdname', default='qstd')
    _p.add_argument('--qretrlmname', default='qretrlm_multifreq')
    _p.add_argument('--wretrlmname', default='wretrlm_multifreq')
    _p.add_argument('--qrealname', default='qreal')
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
        with open(os.path.join('dump', '{}.dump'.format(_name)), 'wb') as __dump:
            dill.dump(_obj, __dump, recurse=True)
        print(colored('...dill', 'green'))


if __name__ == '__main__':
    parser = createArgParser()
    ns = parser.parse_args(sys.argv[1:])
    dump_dir = ns.path_to_dump_dir
    tcl = float(ns.tcl)

    print(colored('\nDUMP dir is {}'.format(dump_dir), 'blue'))

    ID = np.load(os.path.join(dump_dir, 'id.npy'))
    BT = np.load(os.path.join(dump_dir, 'bt.npy'))
    LM, MS = np.asarray([]), np.asarray([])
    if int(ns.lm):
        LM = np.load(os.path.join(dump_dir, 'lm.npy'))
    if int(ns.ms):
        MS = np.load(os.path.join(dump_dir, 'ms.npy'))

    print('\nРазмерности и типы входных данных')
    print(
        ' ID ', ID.shape, ID.dtype, '\n',
        'BT ', BT.shape, BT.dtype, '\n',
    )
    
    if int(ns.lm):
        print(' LM ', LM.shape, LM.dtype, '\n')
        
    alt = np.linspace(0.1, 15., 1000)
    if int(ns.ms):
        print(' MS ', MS.shape, MS.dtype, '\n')

        with open('Dolgoprudnyj_gridded.dump', 'rb') as _dump:
            meteosonde_data = dill.load(_dump)

        _, _, _, alt = meteosonde_data[tuple(MS[0])]

    print("Средняя эффективная температура облака t_cl = {}".format(tcl))

    K_W = np.asarray([kw(nu, t=tcl) for nu in frequencies])

    QSTD, QREAL = np.asarray([]), np.asarray([])
    QRETRLM, WRETRLM = np.asarray([]), np.asarray([])
    QRETRMS, WRETRMS = np.asarray([]), np.asarray([])
    if int(ns.lm):
        QSTD = np.zeros(ID.shape)
        QRETRLM, WRETRLM = np.zeros(ID.shape), np.zeros(ID.shape)
    if int(ns.ms):
        QREAL = np.zeros(ID.shape)
        QRETRMS, WRETRMS = np.zeros(ID.shape), np.zeros(ID.shape)

    progress = 0.
    unique_ids = np.unique(ID)

    print()

    def process(session_id):
        cond = (ID == session_id)

        batch_size = np.count_nonzero(cond)
        # print(batch_size)

        id_, bt = ID[cond], BT[cond]

        stdAtm = Atmosphere.Standard()
        realAtm = Atmosphere.Standard()

        qstd, qreal = None, None

        if int(ns.lm):
            lm = LM[cond]
            T0, P0, rho0 = lm[:, 0], lm[:, 1], lm[:, 2]

            stdAtm = Atmosphere.Standard(T0=T0, P0=P0, rho0=rho0, H=15, dh=15. / 1000)

            del T0
            del P0
            del rho0

            stdAtm.temperature = math.move_axis(math.as_tensor([math.transpose(stdAtm.temperature)]), 0, 1)
            stdAtm.pressure = math.move_axis(math.as_tensor([math.transpose(stdAtm.pressure)]), 0, 1)
            stdAtm.absolute_humidity = math.move_axis(math.as_tensor([math.transpose(stdAtm.absolute_humidity)]), 0, 1)
            stdAtm.liquid_water = math.move_axis(math.as_tensor([math.transpose(stdAtm.liquid_water)]), 0, 1)

            qstd = np.asarray(stdAtm.Q)[:, 0]

        if int(ns.ms):
            ms = MS[cond]
            T, P, rho_rel = [], [], []
            for i in range(len(ms)):
                T_, P_, rho_rel_, _ = meteosonde_data[tuple(ms[i])]
                T.append(T_)
                P.append(P_)
                rho_rel.append(rho_rel_)
            T, P, rho_rel = np.moveaxis(np.asarray([T]), 0, 1), np.moveaxis(np.asarray([P]), 0, 1), \
                np.moveaxis(np.asarray([rho_rel]), 0, 1)

            realAtm = Atmosphere(T, P, RelativeHumidity=rho_rel, altitudes=alt)

            del T
            del P
            del rho_rel

            qreal = np.asarray(realAtm.Q)[:, 0]

        k_w = math.move_axis(math.as_tensor([[K_W[:]] * batch_size]), 0, 1)  # (batch_size, 1, 47)

        brt = math.as_tensor([bt])  # под углом (1, batch_size, 47)
        brt = math.move_axis(brt, 0, 1)  # (batch_size, 1, 47)

        qretrlm, wretrlm = None, None
        qretrms, wretrms = None, None

        if int(ns.lm):
            # MULTI FREQ LOCALMETEO
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

            M_std = math.as_tensor([k_rho_std, k_w])  # (2, batch_size, 1, 47)
            M_std = math.move_axis(M_std, 0, -1)  # (batch_size, 1, 47, 2)

            right_std = math.move_axis(math.as_tensor([tau_e_std - tau_o_std]), 0, -1)  # (batch_size, 1, 47, 1)

            M_std = tf.convert_to_tensor(M_std)
            right_std = tf.convert_to_tensor(right_std)

            # sol_std = math.linalg_lstsq(M_std, right_std)  # (batch_size, 1, 2, 1)
            sol_std = tf.linalg.lstsq(M_std, right_std)

            _Q = sol_std[:, 0, 0, 0]
            _W = sol_std[:, 0, 1, 0]

            qretrlm = math.as_tensor(_Q)
            wretrlm = math.as_tensor(_W)

            if int(ns.correction):
                W0 = math.min_(_W)
                if W0 < 0:
                    d_tau = -1 * k_w * W0
                    _tau_rho = math.move_axis(math.move_axis(k_rho_std, 0, -1) * _Q, -1, 0)
                    qretrlm = math.mean((_tau_rho - d_tau) / k_rho_std, axis=-1)[:, 0]
                    tau_rho = math.move_axis(math.move_axis(k_rho_std, 0, -1) * qretrlm, -1, 0)
                    wretrlm = np.mean((tau_e_std - tau_o_std - tau_rho) / k_w, axis=-1)[:, 0]

            del t_avg_down_std
            del tau_o_std, tau_e_std
            del k_rho_std
            del M_std, right_std, sol_std
            del _Q, _W

        if int(ns.ms):
            # MULTI FREQ METEOSONDE
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

            M_real = math.as_tensor([k_rho_real, k_w])  # (2, batch_size, 1, 47)
            M_real = math.move_axis(M_real, 0, -1)  # (batch_size, 1, 47, 2)

            right_real = math.move_axis(math.as_tensor([tau_e_real - tau_o_real]), 0, -1)  # (batch_size, 1, 47, 1)

            M_real = tf.convert_to_tensor(M_real)
            right_real = tf.convert_to_tensor(right_real)

            # sol_real = math.linalg_lstsq(M_real, right_real)  # (batch_size, 1, 2, 1)
            sol_real = tf.linalg.lstsq(M_real, right_real)

            _Q = sol_real[:, 0, 0, 0]
            _W = sol_real[:, 0, 1, 0]

            qretrms = math.as_tensor(_Q)
            wretrms = math.as_tensor(_W)

            if int(ns.correction):
                W0 = math.min_(_W)
                if W0 < 0:
                    d_tau = -1 * k_w * W0
                    _tau_rho = math.move_axis(math.move_axis(k_rho_real, 0, -1) * _Q, -1, 0)
                    qretrms = math.mean((_tau_rho - d_tau) / k_rho_real, axis=-1)[:, 0]
                    tau_rho = math.move_axis(math.move_axis(k_rho_real, 0, -1) * qretrms, -1, 0)
                    wretrms = np.mean((tau_e_real - tau_o_real - tau_rho) / k_w, axis=-1)[:, 0]

            del t_avg_down_real
            del tau_o_real, tau_e_real
            del k_rho_real
            del M_real, right_real, sol_real
            del _Q, _W

        del k_w, brt
        del stdAtm, realAtm

        return session_id, qstd, qretrlm, wretrlm, qreal, qretrms, wretrms

    n_workers = int(ns.nworkers)

    results = []

    with Pool(processes=n_workers) as pool:
        for result in tqdm.tqdm(pool.imap_unordered(process, unique_ids), total=len(unique_ids)):
            results.append(result)

    for _session_id, _qstd, _qretrlm, _wretrlm, _qreal, _qretrms, _wretrms in results:
        _cond = (ID == _session_id)
        if int(ns.lm):
            QSTD[_cond] = _qstd
            QRETRLM[_cond] = _qretrlm
            WRETRLM[_cond] = _wretrlm
        if int(ns.ms):
            QREAL[_cond] = _qreal
            QRETRMS[_cond] = _qretrms
            WRETRMS[_cond] = _wretrms

    print('\nСохраняем...')

    if int(ns.lm):
        np.save(os.path.join(dump_dir, '{}'.format(ns.qstdname)), QSTD)
        np.save(os.path.join(dump_dir, '{}'.format(ns.qretrlmname)), QRETRLM)
        np.save(os.path.join(dump_dir, '{}'.format(ns.wretrlmname)), WRETRLM)
    if int(ns.ms):
        np.save(os.path.join(dump_dir, '{}'.format(ns.qrealname)), QREAL)
        np.save(os.path.join(dump_dir, '{}'.format(ns.qretrmsname)), QRETRMS)
        np.save(os.path.join(dump_dir, '{}'.format(ns.wretrmsname)), WRETRMS)
