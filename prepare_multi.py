
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

reports = os.listdir(reports_dir)


def process(_report_names, _n):
    _out_ = []

    for report_name in _report_names:
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

                # timestamp = timestamp

                radiometry = np.asarray([float(e) for i, e in enumerate(line) if e and 0 < i < 48], dtype=np.float32)

                localmeteo = np.asarray([T, P, hum, wind, rain], dtype=np.float32)

                meteosonde = np.asarray(r_key, dtype=int)

                _out_.append([timestamp, radiometry, localmeteo, meteosonde])

        _n.value += 1
        print(colored('\r{:.3f}%'.format(_n.value / len(reports) * 100), 'green'), flush=True, end='          ')

    return _out_


if __name__ == '__main__':

    with open('Dolgoprudnyj.dump', 'wb') as dump:
        meteosonde_data = dill.load(dump)
    m_keys = list(meteosonde_data.keys())

    reports = reports[::]

    n_workers = 32
    out = list()
    with Manager() as manager:
        n = manager.Value('d', 0)

        with Pool(processes=n_workers) as pool:
            for report_names in np.array_split(reports, n_workers):
                res = pool.apply_async(func=process, args=(report_names, n, ))
                out.extend(res.get())

    print('\ncreating a dump..')
    with open('DATA.bin', 'wb') as dump:
        dill.dump(np.asarray(out, dtype=object), dump, recurse=True)
