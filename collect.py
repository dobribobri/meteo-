import os
import re
import dill
import ftplib
from settings import Settings
from measurement import Measurement
from termcolor import colored
from multiprocessing import Process, Manager

n_procs = 16


def process(_command, _k):
    print(colored(_command, 'blue'))

    os.system(_command)

    _k.value += 1
    print(colored('=========================================================================================', 'green'))
    print(colored('{:.3f} %'.format(_k.value / N * 100), 'green'))
    print(colored('=========================================================================================', 'green'))


ftp = ftplib.FTP(Settings.Server.IP)
ftp.login(Settings.Server.login, Settings.Server.password)

ls = []
for year in sorted(Settings.Server.year_path.keys()):
    ftp.cwd(Settings.Server.year_path[year])
    ftp.dir(ls.append)

ls = [re.split(" ", item)[-1] for item in ls]
ls = [item for item in ls if item.find('.rar') != -1]
_dt_ = []
for item in ls:
    try:
        _dt_.append(Measurement.decompose(item))
    except ValueError:
        continue

# os.chdir('..')
print(os.getcwd())
# os.system('python3 main.py --update_calibr')

N = len(_dt_) - 1

with Manager() as manager:
    k = manager.Value('d', 0)

    processes = []
    for i in range(N-2, -1, -1):
        c, n = _dt_[i], _dt_[i + 1]

        lbl = c.strftime(Settings.radiometerPrefix + '__%Y.%m.%d_%H_%M_%S_') + \
            n.strftime('_%Y.%m.%d_%H_%M_%S') + '.tb.txt'
        if os.path.exists(os.path.join('full_spec_data', 'tb', lbl)):
            k.value += 1
            continue

        if str(c.year) == '2023':
            continue

        command = 'python3 main.py --range ' + \
                  '-Y {} -M {} -D {} '.format(c.year, c.month, c.day) + \
                  '--hh {} --mm {} --ss {} '.format(c.hour, c.minute, c.second) + \
                  '--Y1 {} --M1 {} --D1 {} '.format(n.year, n.month, n.day) + \
                  '--H1 {} --m1 {} --s1 {} '.format(n.hour, n.minute, n.second) + \
                  '--nosf --noweather --noqw --noplots ' + \
                  '--tbreport --reportroot \'./full_spec_data/\''

        p = Process(target=process, args=(command, k))
        processes.append(p)

    for i in range(0, len(processes), n_procs):
        for j in range(i, i + n_procs):
            if j < len(processes):
                processes[j].start()
        for j in range(i, i + n_procs):
            if j < len(processes):
                processes[j].join()
