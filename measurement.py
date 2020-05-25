# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from datetime import datetime, timedelta, date, time
from settings import Settings
import os
import re
import ftplib
from termcolor import colored
from pyunpack import Archive
import binaryparser  # C++
from collections import defaultdict
from txtparser import TFile
from borland.datetime import TDateTime
import sys
from interquartile import Eliminate
from default import parameter


class Measurement:
    @staticmethod
    def __exist_local(_mlbl: str, mode: str = 't'):
        if mode == 't':
            return os.path.exists(os.path.join(Settings.tfdataDir, _mlbl + '.txt'))
        if mode == 'r':
            return os.path.exists(os.path.join(Settings.bfdataDir, _mlbl + '.rar'))
        if mode == 'd':
            return os.path.exists(os.path.join(Settings.bfdataDir, _mlbl + '.dat'))
        return False

    @staticmethod
    def construct_ftp_path(_mlbl: str):
        year_path = ''
        try:
            year_path = Settings.Server.year_path[int(_mlbl[5:9])]
        except KeyError:
            print('Нет информации о {} годе\t'.format(_mlbl[5:9]) + '[' + colored('Error', 'red') + ']')
            exit(2007)
        ftp_path_ = os.path.join(year_path, _mlbl + '.rar')
        print('Путь к данным на сервере: {}'.format(ftp_path_))
        return ftp_path_

    @staticmethod
    def decompose_mlbl(_mlbl: str, _to_int=False):
        # P22M_2017_08_01__05-09-34 - шаблон метки измерительного сеанса
        stY, stM, stD, sth, stm, sts = \
            _mlbl[5:9], _mlbl[10:12], _mlbl[13:15], \
            _mlbl[17:19], _mlbl[20:22], _mlbl[23:25]
        if _to_int:
            return int(stY), int(stM), int(stD), int(sth), int(stm), int(sts)
        return stY, stM, stD, sth, stm, sts

    @staticmethod
    def find_calibr(_mlbl: str):
        # calibr23_19_03_05_К.p22m - шаблон названия калибровочного файла (год|месяц|день)
        cflist = os.listdir(Settings.cfdataDir)
        _k = dict()
        for i in range(len(cflist)):
            rem = cflist[i]
            cflist[i] = re.sub(r'_К', '', cflist[i])  # "К" написано кириллицей
            if cflist[i] != rem:
                _k[cflist[i]] = 1
            else:
                _k[cflist[i]] = 0
        stY, stM, stD, *_ = Measurement.decompose_mlbl(_mlbl)
        assumed = Settings.calibrPrefix + '_' + \
                  stY[2:] + '_' + stM + '_' + stD + '.' + Settings.calibrPostfix
        # print(assumed)
        cflist = sorted(cflist)
        # print(cflist)
        if assumed <= cflist[0]:
            if _k[cflist[0]]:
                return os.path.join(Settings.cfdataDir, re.sub('.p22m', r'_К.p22m', cflist[0]))
            else:
                return os.path.join(Settings.cfdataDir, cflist[0])
        for i in range(len(cflist) - 1, -1, -1):
            # print('{} > {} -- {}'.format(assumed, cflist[i], assumed > cflist[i]))
            if assumed > cflist[i]:
                if _k[cflist[i]]:
                    return os.path.join(Settings.cfdataDir, re.sub('.p22m', r'_К.p22m', cflist[i]))
                else:
                    return os.path.join(Settings.cfdataDir, cflist[i])
        return ''

    @staticmethod
    def __daterange(start_date, stop_date):
        for n in range(int((stop_date - start_date).days) + 1):
            yield start_date + timedelta(n)

    def __init__(self, datetime_start: datetime = datetime(2017, 8, 1, 5, 9, 34),
                 datetime_stop: datetime = None, erase=False, tfparsemode = '', noconnection=False):
        print(noconnection)
        global ftp
        if not os.path.exists(Settings.bfdataDir):
            os.makedirs(Settings.bfdataDir)
        if not os.path.exists(Settings.tfdataDir):
            os.makedirs(Settings.tfdataDir)

        self.DATA = defaultdict(list)
        self.start_date = date(datetime_start.year, datetime_start.month, datetime_start.day)
        self.start_t = TDateTime(datetime_start.year, datetime_start.month, datetime_start.day,
                                 datetime_start.hour, datetime_start.minute, datetime_start.second).toDouble()
        if datetime_stop:
            self.stop_date = date(datetime_stop.year, datetime_stop.month, datetime_stop.day)
            self.stop_t = TDateTime(datetime_stop.year, datetime_stop.month, datetime_stop.day,
                                    datetime_stop.hour, datetime_stop.minute, datetime_stop.second).toDouble()
        else:
            self.stop_date = self.start_date
            self.stop_t = TDateTime(datetime_start.year, datetime_start.month, datetime_start.day,
                                    hh=23, mm=59, ss=59, ms=999).toDouble()
        # подключение к серверу баз данных
        if not noconnection:
            ftp = ftplib.FTP(Settings.Server.IP)
            ftp.login(Settings.Server.login, Settings.Server.password)
            print('Подключение к серверу\t' + '[' + colored('OK', 'green') + ']')
        mlbls = []
        if noconnection:
            mlbls.append(Measurement.construct_mlbl_(datetime_start))
        for d in Measurement.__daterange(self.start_date, self.stop_date):
            ls = []
            if not noconnection:
                ftp.cwd(Settings.Server.year_path[d.year])
                ftp.dir(ls.append)
            for item in ls:
                arr = re.split(' ', item)
                p = str(arr[len(arr) - 1])
                if (p.find('.rar') != -1) and \
                        (p.find(
                            d.strftime(Settings.radiometerPrefix + '_%Y_%m_%d__')
                        ) != -1):
                    _, _, _, h, _, _ = Measurement.decompose_mlbl(p, _to_int=True)
                    if h + 4 < datetime_start.hour or \
                            (datetime_stop is not None and h - 4 > datetime_stop.hour):
                        continue
                    mlbls.append(re.sub('.rar', '', p))
        if datetime_stop is None:
            mlbls = [mlbl for mlbl in mlbls if mlbl == Measurement.construct_mlbl_(datetime_start)]
        self.tfiles = []
        print(mlbls)
        for mlbl in mlbls:
            print('Метка измерительного сеанса: {}'.format(mlbl))
            ftp = ftplib.FTP(Settings.Server.IP)
            ftp.login(Settings.Server.login, Settings.Server.password)
            # путь до сжатого бинарного файла в локальном хранилище
            rarfile_local_path = os.path.join(Settings.bfdataDir, mlbl + '.rar')
            # путь до распакованного бинарного файла в локальном хранилище
            datfile_local_path = re.sub('.rar', '.dat', rarfile_local_path)
            # путь до текстового файла измерений в локальном хранилище
            txtfile_local_path = os.path.join(Settings.tfdataDir, mlbl + '.txt')

            exist_txt = Measurement.__exist_local(mlbl, mode='t')
            exist_dat = Measurement.__exist_local(mlbl, mode='d')
            exist_rar = Measurement.__exist_local(mlbl, mode='r')

            if not exist_txt and not exist_dat and not exist_rar:
                # В локальном хранилище ничего не найдено. Загрузка данных с сервера
                ftp_path = Measurement.construct_ftp_path(mlbl)
                # выгрузка сжатого бинарного файла
                # с сервера баз данных в локальное хранилище
                try:
                    with open(rarfile_local_path, 'wb') as rarfile:
                        ftp.retrbinary('RETR ' + ftp_path, rarfile.write)
                except ftplib.all_errors:   # !!
                    print('Ошибка FTP. Не удалось загрузить файл\t' + '[' + colored('Error', 'red') + ']')
                    # Удалим обрывок файла, если не удалось загрузить
                    if os.path.exists(rarfile_local_path):
                        os.remove(rarfile_local_path)
                    exit(4)
                print('Загрузка файлов с сервера\t' + '[' + colored('OK', 'green') + ']')
                exist_rar = True

            if not exist_txt and not exist_dat and exist_rar:
                # В локальном хранилище имеется только сжатый бинарник
                # распаковка сжатого бинарного файла в локальном хранилище
                Archive(rarfile_local_path).extractall(Settings.bfdataDir)
                # Если в распакованном архиве была вложенная папка ('P22M/измерение.dat') :
                if os.path.exists(os.path.join(Settings.bfdataDir, Settings.radiometerPrefix, mlbl + '.dat')):
                    os.rename(os.path.join(Settings.bfdataDir, Settings.radiometerPrefix, mlbl + '.dat'),
                              datfile_local_path)
                    os.rmdir(os.path.join(Settings.bfdataDir, Settings.radiometerPrefix))
                # Проверяем, что распаковка удалась
                if not os.path.exists(datfile_local_path):
                    print('Ошибка распаковщика\t' + '[' + colored('Error', 'red') + ']')
                    exit(5)
                else:
                    exist_dat = True

            if not exist_txt and exist_dat:
                # В локальном хранилище найден .dat-файл - распакованный бинарник
                # Найдём нужный калибровочный файл
                calibrfile_path = Measurement.find_calibr(mlbl)
                print('Ближайший по дате файл калибровки: {}'.format(calibrfile_path))

                # Распарсим бинарник в txt-файл и одновременно проведём (первичную) калибровку
                binaryparser.parse(datfile_local_path, calibrfile_path, txtfile_local_path)

                # удалим распакованный .dat-файл (весит много)
                if os.path.exists(datfile_local_path):
                    os.remove(datfile_local_path)

            print(tfparsemode)
            tfile = TFile(txtfile_local_path, mode=tfparsemode)
            tfile.parse(shift=True, rm_zeros=False, sort_freqs=False, sort_time=False,
                        outliers_elimination=False, upper_threshold_val=None)
            self.tfiles.append(tfile)

            if int(erase):
                if os.path.exists(rarfile_local_path):
                    os.remove(rarfile_local_path)
                if os.path.exists(datfile_local_path):
                    os.remove(datfile_local_path)
                if os.path.exists(txtfile_local_path):
                    os.remove(txtfile_local_path)
                print('Очищено.')

    def getDATA(self, rm_zeros=parameter.parsing.measurements.rm_zeros,
                sort_freqs=parameter.parsing.measurements.sort_freqs,
                sort_time=parameter.parsing.measurements.sort_time,
                outliers_elimination=parameter.parsing.measurements.outliers_elimination,
                upper_threshold_val=parameter.parsing.measurements.upper_threshold_val):
        self.DATA.clear()
        for tfile in self.tfiles:
            tfile.cutDATA(start_t=self.start_t, stop_t=self.stop_t)

            if rm_zeros:
                print('Удаление нулей...\t')
                tfile.remove_time_zeros()
                tfile.remove_val_zeros()
            if sort_freqs:
                print('Сортировка по частотам...\t')
                tfile.sort_frequencies()
            if sort_time:
                print('Сортировка по времени...\t')
                tfile.sort_time()
            if outliers_elimination:
                print('Устранение явных выбросов...\t')
                tfile.outliers_elimination(threshold_percentage=None)
            if upper_threshold_val:
                print('Устранение значений выше порогового...\t')
                tfile.upper_threshold_elimination(parameter.parsing.measurements.upper_threshold_val)

            for freq in tfile.DATA.keys():
                self.DATA[freq] += tfile.DATA[freq]

        self.getTimeBounds()
        return self.DATA

    def getTimeBounds(self):
        min_t, max_t = sys.maxsize, 0
        for key in self.DATA.keys():
            for t, _ in self.DATA[key]:
                if t < min_t:
                    min_t = t
                if t > max_t:
                    max_t = t
        return min_t, max_t

    @staticmethod
    def construct_mlbl_(_datetime: datetime):
        _mlbl = _datetime.strftime(Settings.radiometerPrefix + '_%Y_%m_%d__%H-%M-%S')
        return _mlbl

    # def remove_zeros(self):
    #     data = defaultdict(list)
    #     for freq in self.DATA.keys():
    #         for time, val in self.DATA[freq]:
    #             if (time != 0) and (val != 0):
    #                 data[freq].append((time, val))
    #             else:
    #                 print(colored('Удаление единичного измерения. ' +
    #                               'Частота: {}\t Время {} (TDateTime)\t Значение {}'.format(
    #                                   freq, time, val
    #                               ), 'red'))
    #     self.DATA = data
    #     return
    #
    # def sort_frequencies(self):
    #     data = defaultdict(list)
    #     for freq in sorted(self.DATA.keys()):
    #         data[freq] = self.DATA[freq]
    #     self.DATA = data
    #     return
    #
    # def sort_time(self):
    #     for freq in self.DATA.keys():
    #         self.DATA[freq] = sorted(self.DATA[freq], key=lambda t: t[0])
    #     return
    #
    # def remove_time_zeros(self):
    #     data = defaultdict(list)
    #     errors = 0
    #     for freq in self.DATA.keys():
    #         for t, val in self.DATA[freq]:
    #             if t != 0:
    #                 data[freq].append((t, val))
    #             else:
    #                 errors += 1
    #     if errors:
    #         print(colored('Единичных измерений с нулевым значением времени: {}'.format(errors), 'red'))
    #     self.DATA = data
    #     return
    #
    # def remove_val_zeros(self):
    #     data = defaultdict(list)
    #     errors = 0
    #     for freq in self.DATA.keys():
    #         for t, val in self.DATA[freq]:
    #             if val != 0:
    #                 data[freq].append((t, val))
    #             else:
    #                 errors += 1
    #     if errors:
    #         print(colored('Единичных измерений с нулевым значением температуры: {}'.format(errors), 'red'))
    #     self.DATA = data
    #     return
    #
    # def outliers_elimination(self, threshold_percentage: float = None):
    #     for freq in self.DATA.keys():
    #         self.DATA[freq] = Eliminate.time_series(self.DATA[freq], threshold_percentage)
    #     return

    # @staticmethod
    # def construct_mlbl(stY: str = '2017', stM: str = '08', stD: str = '01',
    #                    sth: str = '05', stm: str = '09', sts: str = '34'):
    #     mlbl = Settings.radiometerPrefix + '_' + stY + '_' + stM + '_' + stD + \
    #             '__' + sth + '-' + stm + '-' + sts
    #     print('Метка измерительного сеанса: {}'.format(mlbl))
    #     return mlbl
