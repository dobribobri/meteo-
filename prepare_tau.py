
import numpy as np
import os
import dill
import sys
import argparse
import time
from termcolor import colored

sys.path.append('../atmrad')
from gpu.atmosphere import Atmosphere, avg
import gpu.core.math as math


# radiometry_angle = 51.*np.pi/180
radiometry_angle = 0.

frequencies = np.linspace(18.0, 27.2, 47, endpoint=True)

T_cosmic = 2.72548


def createArgParser():
    _p = argparse.ArgumentParser()
    _p.add_argument('-P', '--path_to_dump_dir', default='./dump/',
                    help='Where to get data from?')
    return _p


def dump(_obj, _path_to_dump_dir, _name, _dump_options):
    if not os.path.exists(_path_to_dump_dir):
        os.makedirs(_path_to_dump_dir)
    print(colored('{}...'.format(_name), 'blue'))
    if 'numpy' in _dump_options:
        np.save(os.path.join(_path_to_dump_dir, '{}.npy'.format(_name)), _obj)
        print(colored('...numpy', 'green'))
    if 'dill' in _dump_options:
        with open(os.path.join(_path_to_dump_dir, '{}.dump'.format(_name)), 'wb') as _dump:
            dill.dump(_obj, _dump, recurse=True)
        print(colored('...dill', 'green'))


if __name__ == '__main__':

    parser = createArgParser()
    ns = parser.parse_args(sys.argv[1:])
    dump_dir = ns.path_to_dump_dir

    print(colored('\nDUMP dir is {}'.format(dump_dir), 'blue'))

    BT = np.load(os.path.join(dump_dir, 'bt.npy'))
    LM = np.load(os.path.join(dump_dir, 'lm.npy'))

    print('\nРазмерности и типы входных данных')
    print(
        'BT ', BT.shape, BT.dtype, '\n',
        'LM ', LM.shape, LM.dtype, '\n',
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

    TAU = np.asarray([[]] * len(frequencies))

    progress = 0.
    n_batches = len(BT) // batch_size

    for n in range(n_batches):
        indexes = list(range(len(BT)))[n * batch_size: n * batch_size + batch_size]

        start = time.time()

        T0, P0, rho0 = [], [], []
        for i in indexes:
            T0_, P0_, rho0_, *_ = LM[i]

            T0.append(T0_)
            P0.append(P0_)
            rho0.append(rho0_)

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

        brt = math.as_tensor([[BT[i, :]] for i in indexes])  # под углом | (batch_size, 1, 47)

        t_avg_down_std = math.as_tensor(
            [avg.downward.T(stdAtm, nu, radiometry_angle) for nu in frequencies]
        )  # под углом | (47, batch_size, 1)
        t_avg_down_std = math.move_axis(t_avg_down_std, 0, -1)  # (batch_size, 1, 47)

        tau_e_std = math.log(
            (t_avg_down_std - T_cosmic) / (t_avg_down_std - brt)
        ) * math.cos(radiometry_angle)  # (batch_size, 1, 47) - в зените

        TAU = np.hstack((TAU, np.asarray(tau_e_std[:, 0, :], dtype=np.float32).T))

        dump(_obj=np.asarray(TAU, dtype=np.float32).T,
             _path_to_dump_dir=dump_dir,
             _name='tau',
             _dump_options=['numpy']
        )

        del stdAtm
        del brt
        del t_avg_down_std
        del tau_e_std

        progress += len(indexes)
        end = time.time() - start

        print(colored('Total progress: {:.5f}% \t\t Batch no. {} out of {}\t\t Time spent per batch: {:.4f}'.format(
            progress / len(BT) * 100.,
            n + 1, n_batches,
            end),
            'green')
        )

    print('\nСохраняем...')

    TAU = np.asarray(TAU, dtype=np.float32).T
    dump(_obj=TAU, _path_to_dump_dir=dump_dir, _name='tau', _dump_options=['numpy'])
    dump(_obj=TAU, _path_to_dump_dir=dump_dir, _name='tau', _dump_options=['dill'])
