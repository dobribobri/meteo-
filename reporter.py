#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from collections import defaultdict
from dprinter import printDATA2File
from termcolor import colored
from borland.datetime import Double2TDateTime
import sys
import regex as re
import os


class Reporter:
    def __init__(self, global_report_path: str = ''):
        self.DATA = defaultdict(list)
        self.path = ''
        self.global_report_path = global_report_path
        self.GlobalData = defaultdict(list)

        self.global_report_path_1 = re.sub('.txt', '_1.txt', global_report_path)
        self.GlobalData_1 = defaultdict(list)
        self.lbl = ''

    def set(self, DATA, report_path: str, lbl: str):
        self.DATA = DATA
        self.path = report_path
        self.lbl = lbl

    def makeTbReport(self):
        with open(self.path, 'w') as tbreport:
            tbreport.write('Средние значения яркостных температур\n')
            for freq in self.DATA.keys():
                avg = 0
                min, max = sys.maxsize, -sys.maxsize
                for _, v in self.DATA[freq]:
                    avg += v
                    if v < min:
                        min = v
                    if v > max:
                        max = v
                avg /= len(self.DATA[freq])
                tbreport.write('{}: {:.4f}\n'.format(freq, avg))

                self.GlobalData[(self.lbl, freq)] += [avg, min, max, max-min]

            tbreport.write('\n')
            tbreport.write('Данные:\n')
            printDATA2File(DATA=self.DATA, File=tbreport, shortened=True, columns=5)
        print('Отчёт сохранён\t' + '[' + colored('OK', 'green') + ']')
        return

    def makeSFReport(self):
        DATA = defaultdict(list)
        for freq in self.DATA.keys():
            for t, v in self.DATA[freq]:
                time = Double2TDateTime(t)
                time = time.ss + 60 * time.mm + time.ms / 1000
                DATA[freq].append((time, v))
        min25, max25 = sys.maxsize, -sys.maxsize
        fmin25, fmax25 = 0, 0
        min30, max30 = sys.maxsize, -sys.maxsize
        fmin30, fmax30 = 0, 0
        min50, max50 = sys.maxsize, -sys.maxsize
        fmin50, fmax50 = 0, 0
        min60, max60 = sys.maxsize, -sys.maxsize
        fmin60, fmax60 = 0, 0
        min100, max100 = sys.maxsize, -sys.maxsize
        fmin100, fmax100 = 0, 0
        min150, max150 = sys.maxsize, -sys.maxsize
        fmin150, fmax150 = 0, 0
        min200, max200 = sys.maxsize, -sys.maxsize
        fmin200, fmax200 = 0, 0
        # print(DATA[18.0])
        for freq in DATA.keys():
            val25, val30, val50, val60, val100, val150, val200 = 0, 0, 0, 0, 0, 0, 0
            k25, k30, k50, k60, k100, k150, k200 = 0, 0, 0, 0, 0, 0, 0
            for sec, val in DATA[freq]:
                if 18 < sec < 27:
                    val25 += val
                    k25 += 1
                if 28 < sec < 38:
                    val30 += val
                    k30 += 1
                if 44 < sec <= 60:
                    # print('found 55s. val')
                    val50 += val
                    k50 += 1
                if 61 <= sec < 77:
                    val60 += val
                    k60 += 1
                if 94 < sec < 104:
                    val100 += val
                    k100 += 1
                if 149 < sec < 159:
                    val150 += val
                    k150 += 1
                if 193 < sec < 203:
                    val200 += val
                    k200 += 1
            if k25:
                val25 /= k25
            if k30:
                val30 /= k30
            if k50:
                val50 /= k50
            if k60:
                val60 /= k60
            if k100:
                val100 /= k100
            if k150:
                val150 /= k150
            if k200:
                val200 /= k200

            # print([val25, val30, val50, val60, val100, val150, val200])
            self.GlobalData[(self.lbl, freq)] += [val25, val30, val50, val60, val100, val150, val200]

            if k25 and val25 < min25:
                min25 = val25
                fmin25 = freq
            if k30 and val30 < min30:
                min30 = val30
                fmin30 = freq
            if k50 and val50 < min50:
                min50 = val50
                fmin50 = freq
            if k60 and val60 < min60:
                min60 = val60
                fmin60 = freq
            if k100 and val100 < min100:
                min100 = val100
                fmin100 = freq
            if k150 and val150 < min150:
                min150 = val150
                fmin150 = freq
            if k200 and val200 < min200:
                min200 = val200
                fmin200 = freq
                
            if val25 > max25:
                max25 = val25
                fmax25 = freq
            if val30 > max30:
                max30 = val30
                fmax30 = freq
            if val50 > max50:
                max50 = val50
                fmax50 = freq
            if val60 > max60:
                max60 = val60
                fmax60 = freq
            if val100 > max100:
                max100 = val100
                fmax100 = freq
            if val150 > max150:
                max150 = val150
                fmax150 = freq
            if val200 > max200:
                max200 = val200
                fmax200 = freq
                
        w = [0 for _ in range(28)]
                
        with open(self.path, 'w') as sfreport:
            # printDATA2File(DATA=DATA, File=sfreport, shortened=False, columns=5)
            if max25 != -sys.maxsize and max25 != 0 and min25 != sys.maxsize:
                sfreport.write('Для интервала ~{} сек.\n'.format(25))
                sfreport.write('\tмаксимум {:.2f}, частота {}\n'.format(max25, fmax25))
                sfreport.write('\tминимум {:.2f}, частота {}\n\n'.format(min25, fmin25))
                w[0], w[1], w[2], w[3] = max25, fmax25, min25, fmin25
            if max30 != -sys.maxsize and max30 != 0 and min30 != sys.maxsize:
                sfreport.write('Для интервала ~{} сек.\n'.format(30))
                sfreport.write('\tмаксимум {:.2f}, частота {}\n'.format(max30, fmax30))
                sfreport.write('\tминимум {:.2f}, частота {}\n\n'.format(min30, fmin30))
                w[4], w[5], w[6], w[7] = max30, fmax30, min30, fmin30
            if max50 != -sys.maxsize and max50 != 0 and min50 != sys.maxsize:
                sfreport.write('Для интервала ~{} сек.\n'.format(50))
                sfreport.write('\tмаксимум {:.2f}, частота {}\n'.format(max50, fmax50))
                sfreport.write('\tминимум {:.2f}, частота {}\n\n'.format(min50, fmin50))
                w[8], w[9], w[10], w[11] = max50, fmax50, min50, fmin50
            if max60 != -sys.maxsize and max60 != 0 and min60 != sys.maxsize:
                sfreport.write('Для интервала ~{} сек.\n'.format(60))
                sfreport.write('\tмаксимум {:.2f}, частота {}\n'.format(max60, fmax60))
                sfreport.write('\tминимум {:.2f}, частота {}\n\n'.format(min60, fmin60))
                w[12], w[13], w[14], w[15] = max60, fmax60, min60, fmin60
            if max100 != -sys.maxsize and max100 != 0 and min100 != sys.maxsize:
                sfreport.write('Для интервала ~{} сек.\n'.format(100))
                sfreport.write('\tмаксимум {:.2f}, частота {}\n'.format(max100, fmax100))
                sfreport.write('\tминимум {:.2f}, частота {}\n\n'.format(min100, fmin100))
                w[16], w[17], w[18], w[19] = max100, fmax100, min100, fmin100
            if max150 != -sys.maxsize and max150 != 0 and min150 != sys.maxsize:
                sfreport.write('Для интервала ~{} сек.\n'.format(150))
                sfreport.write('\tмаксимум {:.2f}, частота {}\n'.format(max150, fmax150))
                sfreport.write('\tминимум {:.2f}, частота {}\n\n'.format(min150, fmin150))
                w[20], w[21], w[22], w[23] = max150, fmax150, min150, fmin150
            if max200 != -sys.maxsize and max200 != 0 and min200 != sys.maxsize:
                sfreport.write('Для интервала ~{} сек.\n'.format(200))
                sfreport.write('\tмаксимум {:.2f}, частота {}\n'.format(max200, fmax200))
                sfreport.write('\tминимум {:.2f}, частота {}\n\n'.format(min200, fmin200))
                w[24], w[25], w[26], w[27] = max200, fmax200, min200, fmin200
        print('Отчёт сохранён\t' + '[' + colored('OK', 'green') + ']')

        self.GlobalData_1[self.lbl] = w

        return

    def makeWeatherReport(self):
        w = [0 for _ in range(24)]
        with open(self.path, 'w') as wreport:
            for key in self.DATA.keys():
                avg = 0
                min, max = sys.maxsize, -sys.maxsize
                for _, v in self.DATA[key]:
                    avg += v
                    if v < min:
                        min = v
                    if v > max:
                        max = v
                avg /= len(self.DATA[key])
                s, e = '', ''
                if key == 'temper':
                    s = 'Температура воздуха:'
                    e = '(Cels)'
                    w[0], w[1], w[2], w[3] = avg, min, max, max - min
                if key == 'mmrtst':
                    s = 'Атмосферное давление:'
                    e = '(мм.рт.ст.)'
                    w[4], w[5], w[6], w[7] = avg, min, max, max - min
                if key == 'pr_hpa':
                    s = 'Атмосферное давление:'
                    e = '(гПа)'

                if key == 'rhorel':
                    s = 'Относительная влажность:'
                    e = '(%)'
                    w[12], w[13], w[14], w[15] = avg, min, max, max - min
                if key == 'rhoabs':
                    s = 'Абсолютная влажность:'
                    e = '(г/м3)'
                    w[8], w[9], w[10], w[11] = avg, min, max, max - min
                if key == 'v_wind':
                    s = 'Скорость ветра:'
                    e = '(м/с)'
                    w[16], w[17], w[18], w[19] = avg, min, max, max - min
                if key == 'rainrt':
                    s = 'Кол-во осадков:'
                    e = '(мм)'
                    w[20], w[21], w[22], w[23] = avg, min, max, max - min

                wreport.write('{}\n'.format(s) +
                              'минимум {:.2f} {}\n'.format(min, e) +
                              'среднее {:.2f} {}\n'.format(avg, e) +
                              'максимум {:.2f} {}\n'.format(max, e))

        for key in self.GlobalData.keys():
            self.GlobalData[key] += w

        self.GlobalData_1[self.lbl] += w

        print('Отчёт сохранён\t' + '[' + colored('OK', 'green') + ']')
        return

    def writeGlobal(self):
        if not os.path.exists(self.global_report_path):
            with open(self.global_report_path, 'w') as grfile:
                grfile.write('datetime freq Tb* Tbmin Tbmax deltaTb ' +
                             'sf25 sf30 sf50 sf60 sf100 sf150 sf200 ' +
                             'T* Tmin Tmax deltaT ' +
                             'P* Pmin Pmax deltaP ' +
                             'Rho* Rhomin Rhomax deltaRho ' +
                             'Rho%* Rho%min Rho%max deltaRho% ' +
                             'V* Vmin Vmax deltaV ' +
                             'Pt* Ptmin Ptmax deltaPt\n')
        if not os.path.exists(self.global_report_path_1):
            with open(self.global_report_path_1, 'a') as gr1file:
                gr1file.write('max25 fmax25 min25 fmin25 ' +
                              'max30 fmax30 min30 fmin30 ' +
                              'max50 fmax50 min50 fmin50 ' +
                              'max60 fmax60 min60 fmin60 ' +
                              'max100 fmax100 min100 fmin100 ' +
                              'max150 fmax150 min150 fmin150 ' +
                              'max200 fmax200 min200 fmin200 ' +
                              'T* Tmin Tmax deltaT ' +
                              'P* Pmin Pmax deltaP ' +
                              'Rho* Rhomin Rhomax deltaRho ' +
                              'Rho%* Rho%min Rho%max deltaRho% ' +
                              'V* Vmin Vmax deltaV ' +
                              'Pt* Ptmin Ptmax deltaPt\n')
        with open(self.global_report_path, 'a') as grfile:
            for lbl, freq in self.GlobalData.keys():
                s = '{} {} '.format(lbl, freq)
                # print(self.GlobalData[(lbl, freq)])
                for item in self.GlobalData[(lbl, freq)]:
                    s += '{} '.format(item)
                grfile.write(s[:len(s)-1] + '\n')
        with open(self.global_report_path_1, 'a') as gr1file:
            s = '{} '.format(self.lbl)
            for item in self.GlobalData_1[self.lbl]:
                s += '{} '.format(item)
            gr1file.write(s[:len(s)-1] + '\n')
        return

    def makeFullSFReport(self):
        length = len(self.DATA[18.0])
        with open(self.path, 'w') as file:
            s = 'time '
            for freq in self.DATA.keys():
                s += str(freq) + ' '
            file.write(s[:-1] + '\n')
            for i in range(1, length):
                s = ''
                # t, _ = self.DATA[18.0][i]
                # t = Double2TDateTime(t).strSeconds()
                t = i * 11
                s += str(t) + ' '
                for freq in self.DATA.keys():
                    _, val = self.DATA[freq][i]
                    s += str(val) + ' '
                file.write(s[:-1] + '\n')
        return

    def makeQWReport(self, QDATA, WDATA):
        with open(self.path, 'w') as file:
            file.write('freq_pair Q_avg W_avg Q_max W_max Q_min W_min\n')
            for key in QDATA.keys():
                q_avg, q_max, q_min = 0, 0, sys.maxsize
                w_avg, w_max, w_min = 0, 0, sys.maxsize
                for i in range(len(QDATA[key])):
                    _, q_val = QDATA[key][i]
                    _, w_val = WDATA[key][i]
                    q_avg += q_val
                    w_avg += w_val
                    if q_val > q_max:
                        q_max = q_val
                    if w_val > w_max:
                        w_max = w_val
                    if q_val < q_min:
                        q_min = q_val
                    if w_val < w_min:
                        w_min = w_val
                q_avg /= len(QDATA[key])
                w_avg /= len(QDATA[key])
                file.write(str(key) + ' ' + str(q_avg) + ' ' + str(w_avg) + ' ' +
                           str(q_max) + ' ' + str(w_max) + ' ' + str(q_min) + ' ' + str(w_min) + '\n')






