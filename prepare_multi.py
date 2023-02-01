
import os
import re
import dill
import numpy as np
from termcolor import colored
from borland_datetime import TDateTime
from weather import Weather
from settings import parameter as p
import datetime
from multiprocessing import Pool, Manager

reports_dir = os.path.join('full_spec_data', 'tb')


def process(_report_names, _report_ids, _n):
    _timestamps_ = []
    _pydatetime_ = []
    _radiometry_ = []
    _localmeteo_ = []
    _meteosonde_ = []
    _sessionids_ = []

    for report_name, report_number in zip(_report_names, _report_ids):
        YY = report_name[6:10]
        MM = report_name[11:13]
        DD = report_name[14:16]
        hh = report_name[17:19]
        mm = report_name[20:22]
        ss = report_name[23:25]
        Y1 = report_name[27:31]
        M1 = report_name[32:34]
        D1 = report_name[35:37]
        H1 = report_name[38:40]
        m1 = report_name[41:43]
        s1 = report_name[44:46]

        start = TDateTime(YY, MM, DD, hh, mm, ss)
        stop = TDateTime(Y1, M1, D1, H1, m1, s1)

        m_date = start.toPythonDate()
        if 0 <= int(hh) < 6:
            m_date = m_date - datetime.timedelta(days=1)
            meas = 0
        elif 6 <= int(hh) < 18:
            m_date = m_date
            meas = 12
        else:
            m_date = m_date + datetime.timedelta(days=1)
            meas = 0

        r_key = [m_date.year, m_date.month, m_date.day, meas]
        if tuple(r_key) not in m_keys:
            _n.value += 1
            continue

        weather = Weather(start, stop)

        try:
            weather.apply()
        except Exception as e:
            # print(colored(start.__str__(), 'magenta'))
            # print(colored(e, 'red'))
            # print()
            _n.value += 1
            continue

        with open(os.path.join(reports_dir, report_name), 'r') as report:
            for i, line in enumerate(report):
                if not i:
                    continue
                line = re.split(' ', re.sub(r'[^0-9\. ]', '', line))
                timestamp = float(line[0])
                try:
                    T = weather.Temperature(timestamp, dimension=p.weather.labels.T_C)
                    P = weather.Pressure(timestamp, dimension=p.weather.labels.P_hpa)
                    hum = weather.Rho_abs(timestamp)
                    wind = weather.WindV(timestamp)
                    rain = weather.RainRt(timestamp)
                except Exception as e:
                    # print(colored(TDateTime.fromDouble(timestamp).__str__(), 'blue'))
                    # print(colored(e, 'red'))
                    # print()
                    continue

                if T > 100 or T < -100:
                    continue
                if P < 0 or P > 2000:
                    continue
                if hum > 100 or hum < 0:
                    continue
                if wind < 0 or wind > 100:
                    continue

                _timestamps_.append(timestamp)

                pydt = TDateTime.fromDouble(timestamp).toPythonDateTime()
                pydatetime_ = np.asarray([pydt.year, pydt.month, pydt.day,
                                          pydt.hour, pydt.minute, pydt.second, pydt.microsecond], dtype=int)
                _pydatetime_.append(pydatetime_)

                radiometry_ = np.asarray([float(e) for i, e in enumerate(line) if e and 0 < i < 48], dtype=np.float32)
                _radiometry_.append(radiometry_)

                localmeteo_ = np.asarray([T, P, hum, wind, rain], dtype=np.float32)
                _localmeteo_.append(localmeteo_)

                meteosonde_ = np.asarray(r_key, dtype=int)
                _meteosonde_.append(meteosonde_)

                _sessionids_.append(report_number)

        _n.value += 1
        print(colored('\r{:.3f}%'.format(_n.value / len(reports) * 100), 'green'), flush=True, end='          ')

    return _timestamps_, _pydatetime_, _sessionids_, _radiometry_, _localmeteo_, _meteosonde_


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

    TIMESTAMPS = []
    PYDATETIME = []
    RADIOMETRY = []
    LOCALMETEO = []
    METEOSONDE = []
    SESSIONIDS = []

    with open('Dolgoprudnyj.dump', 'rb') as dump_:
        meteosonde_data = dill.load(dump_)
    m_keys = list(meteosonde_data.keys())

    reports = os.listdir(reports_dir)
    numbers, reports = np.asarray(list(enumerate(reports[::]))).T

    n_workers = 32

    with Manager() as manager:
        n = manager.Value('d', 0)

        with Pool(processes=n_workers) as pool:
            for report_names, report_numbers in zip(np.array_split(reports, n_workers),
                                                    np.array_split(numbers, n_workers)):
                res = pool.apply_async(func=process, args=(report_names, report_numbers, n, ))
                timestamps, pydatetime, sessionids, radiometry, localmeteo, meteosonde = res.get()

                TIMESTAMPS.extend(timestamps)
                PYDATETIME.extend(pydatetime)
                RADIOMETRY.extend(radiometry)
                LOCALMETEO.extend(localmeteo)
                METEOSONDE.extend(meteosonde)
                SESSIONIDS.extend(sessionids)

    print('\n\nCreating dumps..\n')

    # dump(_obj=np.asarray(TIMESTAMPS), _name='timestamps', _dump_options=['numpy', 'dill'])
    # dump(_obj=np.asarray(PYDATETIME, dtype=int), _name='pydatetime', _dump_options=['numpy', 'dill'])
    # dump(_obj=np.asarray(RADIOMETRY, dtype=np.float32), _name='radiometry', _dump_options=['numpy', 'dill'])
    # dump(_obj=np.asarray(LOCALMETEO, dtype=np.float32), _name='localmeteo', _dump_options=['numpy', 'dill'])
    # dump(_obj=np.asarray(METEOSONDE, dtype=int), _name='meteosonde', _dump_options=['numpy', 'dill'])

    dump(_obj=np.asarray(TIMESTAMPS), _name='timestamps', _dump_options=['numpy'])
    dump(_obj=np.asarray(PYDATETIME, dtype=int), _name='pydatetime', _dump_options=['numpy'])
    dump(_obj=np.asarray(RADIOMETRY, dtype=np.float32), _name='radiometry', _dump_options=['numpy'])
    dump(_obj=np.asarray(LOCALMETEO, dtype=np.float32), _name='localmeteo', _dump_options=['numpy'])
    dump(_obj=np.asarray(METEOSONDE, dtype=int), _name='meteosonde', _dump_options=['numpy'])
    dump(_obj=np.asarray(SESSIONIDS, dtype=int), _name='sessionids', _dump_options=['numpy'])

    dump(_obj=np.asarray(TIMESTAMPS), _name='timestamps', _dump_options=['dill'])
    dump(_obj=np.asarray(PYDATETIME, dtype=int), _name='pydatetime', _dump_options=['dill'])
    dump(_obj=np.asarray(RADIOMETRY, dtype=np.float32), _name='radiometry', _dump_options=['dill'])
    dump(_obj=np.asarray(LOCALMETEO, dtype=np.float32), _name='localmeteo', _dump_options=['dill'])
    dump(_obj=np.asarray(METEOSONDE, dtype=int), _name='meteosonde', _dump_options=['dill'])
    dump(_obj=np.asarray(SESSIONIDS, dtype=int), _name='sessionids', _dump_options=['dill'])
