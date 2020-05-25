# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

import csv
import regex as re
import os
import sys
from collections import defaultdict
from settings import Settings
from termcolor import colored


# Функция ищет все файлы с именем f во всех подкаталогах каталога catalog
def find_files(catalog, f):
    find_files_ = []
    for root, dirs, files in os.walk(catalog):
        find_files_ += [os.path.join(root, name) for name in files if name == f]
    return find_files_


def load(MeteoData, base=Settings.meteoBaseDir):
    print('Подождите...')
    # base = './w/'
    # MeteoData = ['meteo_1_2017-01-01_2019-09-01.csv', 'meteo_2_2017-01-01_2019-09-01.csv']
    if not os.path.exists(base):
        for i, csvpath in enumerate(MeteoData):
            with open(csvpath, 'r') as csvfile:
                MeteoDataReader = csv.reader(csvfile, delimiter=',')
                for k, row in enumerate(MeteoDataReader):
                    if not k:
                        continue
                    data = re.split('[/ ]', row[0]) + row[1:7]
                    # data[0] -- year (YYYY)
                    # data[1] -- month (MM)
                    # data[2] -- day (DD)
                    # data[3] -- time (hh:mm)
                    # data[4] -- pressure
                    # data[5] -- temperature
                    # data[6] -- humidity
                    # data[7] -- wind speed
                    # data[8] -- rain rate
                    if not os.path.isdir(os.path.join(base, data[0])):
                        os.makedirs(os.path.join(base, data[0]))
                    if not os.path.isdir(os.path.join(base, data[0], data[1])):
                        os.makedirs(os.path.join(base, data[0], data[1]))
                    if not os.path.isdir(os.path.join(base, data[0], data[1], data[2])):
                        os.makedirs(os.path.join(base, data[0], data[1], data[2]))
                    filePath = os.path.join(base, data[0], data[1], data[2], 'data')
                    with open(filePath, 'a') as file:
                        file.write(data[3] + ' ' + data[4] + ' ' + data[5] + ' ' +
                                   data[6] + ' ' + data[7] + ' ' + data[8] + '\n')
                    if not(k % 1000):
                        sys.stdout.write("Обработано строк: %dк   \r" % (k//1000))
                        sys.stdout.flush()
            print('\nМетеостанция #{}\t'.format(i+1) + '[' + colored('OK', 'green') + ']')
    # if os.path.exists(base):
        print('Дополнительные операции...')
        deleted = 0
        DataList = find_files(base, 'data')
        for datapath in DataList:
            print('{}\tОбработка...'.format(datapath))
            DATA = defaultdict(list)
            with open(datapath, 'r') as datafile:
                for row in datafile:
                    data = re.split(' ', re.sub('\n', '', row))
                    # data[0] -- time (hh:mm)
                    # data[1] -- pressure
                    # data[2] -- temperature
                    # data[3] -- humidity
                    # data[4] -- wind speed
                    # data[5] -- rain rate
                    DATA[data[0]].append(data)
            i = 0
            for time in DATA.keys():
                if len(DATA[time]) > 1:
                    i += 1
                    sdata = []
                    for item in DATA[time]:
                        if len(item) == 6:
                            sdata = item[:]
                    try:
                        P, T, Hum, Wind, RainRt, k = 0., 0., 0., 0., 0., 0
                        for data in DATA[time]:
                            P += float(data[1])
                            T += float(data[2])
                            Hum += float(data[3])
                            Wind += float(data[4])
                            RainRt += float(data[5])
                            k += 1
                        P /= k
                        T /= k
                        Hum /= k
                        Wind /= k
                        RainRt /= k
                        data = ['{:.3f}'.format(time), '{:.3f}'.format(P), '{:.3f}'.format(T),
                                '{:.3f}'.format(Hum), '{:.3f}'.format(Wind), '{:.3f}'.format(RainRt)]
                        DATA[time].clear()
                        DATA[time].append(data)
                    except ValueError:
                        if sdata:
                            DATA[time].clear()
                            DATA[time].append(sdata)
                        else:
                            deleted += len(DATA[time])
                            del DATA[time]
                        continue
            # for time in DATA.keys():
            #     print(DATA[time])
            if i:
                print('Найдено повторяющихся временных меток: {}'.format(i))
            with open(datapath, 'w') as datafile:
                for time in sorted(DATA.keys()):
                    for data in DATA[time]:
                        datafile.write(time + ' ' + data[1] + ' ' + data[2] + ' ' +
                                       data[3] + ' ' + data[4] + ' ' +
                                       data[5] + '\n')
            DATA.clear()
        print('Всего пришлось полностью удалить {} временных меток'.format(deleted))
    print('База метеорологических данных\t['+colored('OK', 'green')+']')
    return
