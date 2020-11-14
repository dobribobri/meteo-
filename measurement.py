# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from session import Session
from borland_datetime import TDateTime, daterange
import binaryparser  # C++
from datetime import datetime, timedelta
from settings import Settings, parameter
from txtparser import TFile
from pyunpack import Archive
import regex as re
import ftplib
import os
from termcolor import colored


class Measurement:
    @staticmethod
    def exist_local(mlbl: str, mode: str = 't') -> bool:
        if mode == 't':
            return os.path.exists(os.path.join(Settings.tfdataDir, mlbl + '.txt'))
        if mode == 'r':
            return os.path.exists(os.path.join(Settings.bfdataDir, mlbl + '.rar'))
        if mode == 'd':
            return os.path.exists(os.path.join(Settings.bfdataDir, mlbl + '.dat'))
        return False

    @staticmethod
    def construct_ftp_path(mlbl: str) -> str:
        year_path = ''
        try:
            year_path = Settings.Server.year_path[int(mlbl[5:9])]
        except KeyError:
            print('No info at {} year\t'.format(mlbl[5:9]) + '[' + colored('Error', 'red') + ']')
            exit(2007)
        ftp_path = os.path.join(year_path, mlbl + '.rar')
        print('Path to data (server): {}'.format(ftp_path))
        return ftp_path

    @staticmethod
    def decompose(mlbl: str) -> datetime:
        # P22M_2017_08_01__05-09-34 - шаблон метки измерительного сеанса
        stY, stM, stD, sth, stm, sts = \
            int(mlbl[5:9]), int(mlbl[10:12]), int(mlbl[13:15]), \
            int(mlbl[17:19]), int(mlbl[20:22]), int(mlbl[23:25])
        return datetime(stY, stM, stD, sth, stm, sts)

    @staticmethod
    def find_calibr(mlbl: str) -> str:
        # calibr23_19_03_05_К.p22m - шаблон названия калибровочного файла (год|месяц|день)
        DT = Measurement.decompose(mlbl)
        stY, stM, stD = DT.strftime("%Y"), DT.strftime("%m"), DT.strftime("%d")
        assumed = Settings.calibrPrefix + '_' + stY[2:] + '_' + stM + '_' + stD + '.' + Settings.calibrPostfix
        cflist = sorted(os.listdir(Settings.cfdataDir))
        for i in range(len(cflist) - 1, -1, -1):
            if assumed > re.sub('_К', '', cflist[i]):    # "К" написано кириллицей
                return os.path.join(Settings.cfdataDir, cflist[i])
        return os.path.join(Settings.cfdataDir, cflist[0])

    def __init__(self, start: datetime = datetime(2017, 8, 1, 5, 9, 34),
                 stop: datetime = None, tfparsemode: str = '',
                 erase_rar=False, erase_dat=True, erase_txt=False):

        if not os.path.exists(Settings.bfdataDir):
            os.makedirs(Settings.bfdataDir)
        if not os.path.exists(Settings.tfdataDir):
            os.makedirs(Settings.tfdataDir)

        if not stop:
            stop = start + timedelta(hours=3)
        start = TDateTime.fromPythonDateTime(start)
        stop = TDateTime.fromPythonDateTime(stop)
        self.start_t = start.toDouble()
        self.stop_t = stop.toDouble()

        ftp = ftplib.FTP(Settings.Server.IP)
        ftp.login(Settings.Server.login, Settings.Server.password)
        print('Connected to server\t' + '[' + colored('OK', 'green') + ']')
        data = []
        for d in daterange(start, stop):
            ls = []
            ftp.cwd(Settings.Server.year_path[d.year])
            ftp.dir(ls.append)
            for item in ls:
                a = re.split(' ', item)
                p = str(a[-1])
                if (p.find('.rar') != -1) and \
                        (p.find(
                            d.strftime(Settings.radiometerPrefix + '_%Y_%m_%d__')
                        ) != -1):
                    m_start = Measurement.decompose(p)
                    m_start_t = TDateTime.fromPythonDateTime(m_start).toDouble()
                    data.append((re.sub('.rar', '', p), m_start_t))
        data = sorted(data, key=lambda tup: tup[1])
        i_start, i_stop = 0, len(data) - 1
        for i in range(len(data)-1):
            _, t = data[i+1]
            if self.start_t < t:
                i_start = i
                break
        for i in range(len(data)-1, -1, -1):
            _, t = data[i]
            if t < self.stop_t:
                i_stop = i
                break

        self.tfiles = []
        for i in range(i_start, i_stop + 1):
            mlbl, _ = data[i]
            print('Measurement session label: {}'.format(mlbl))
            ftp = ftplib.FTP(Settings.Server.IP)
            ftp.login(Settings.Server.login, Settings.Server.password)
            # путь до сжатого бинарного файла в локальном хранилище
            rarfile_local_path = os.path.join(Settings.bfdataDir, mlbl + '.rar')
            # путь до распакованного бинарного файла в локальном хранилище
            datfile_local_path = re.sub('.rar', '.dat', rarfile_local_path)
            # путь до текстового файла измерений в локальном хранилище
            txtfile_local_path = os.path.join(Settings.tfdataDir, mlbl + '.txt')

            exist_txt = Measurement.exist_local(mlbl, mode='t')
            exist_dat = Measurement.exist_local(mlbl, mode='d')
            exist_rar = Measurement.exist_local(mlbl, mode='r')

            if not exist_txt and not exist_dat and not exist_rar:
                # В локальном хранилище ничего не найдено. Загрузка данных с сервера
                ftp_path = Measurement.construct_ftp_path(mlbl)
                # выгрузка сжатого бинарного файла
                # с сервера баз данных в локальное хранилище
                try:
                    with open(rarfile_local_path, 'wb') as rarfile:
                        ftp.retrbinary('RETR ' + ftp_path, rarfile.write)
                except ftplib.all_errors:
                    print('FTP error\t' + '[' + colored('Error', 'red') + ']')
                    # Удалим обрывок файла, если не удалось загрузить
                    if os.path.exists(rarfile_local_path):
                        os.remove(rarfile_local_path)
                    exit(4)
                print('Uploading files from server\t' + '[' + colored('OK', 'green') + ']')
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
                    print('Unpacking error\t' + '[' + colored('Error', 'red') + ']')
                    exit(5)
                else:
                    exist_dat = True

            if not exist_txt and exist_dat:
                # В локальном хранилище найден .dat-файл - распакованный бинарник
                # Найдём нужный калибровочный файл
                calibrfile_path = Measurement.find_calibr(mlbl)
                print('Closest calibration file: {}'.format(calibrfile_path))

                # Распарсим бинарник в txt-файл и одновременно проведём (первичную) калибровку
                binaryparser.parse(datfile_local_path, calibrfile_path, txtfile_local_path)

            if exist_rar and erase_rar:
                os.remove(rarfile_local_path)
            if exist_dat and erase_dat:
                os.remove(datfile_local_path)

            print(tfparsemode)
            tfile = TFile(txtfile_local_path, mode=tfparsemode)
            self.tfiles.append(tfile)
        self.erase_txt = erase_txt
        self.DATA = self.getData()

    def getData(self, frequencies: list = None) -> Session:
        MDATA = Session()
        for tfile in self.tfiles:
            tfile.parse(True,
                        parameter.parsing.measurements.rm_zeros,
                        parameter.parsing.measurements.sort_freqs,
                        parameter.parsing.measurements.sort_time,
                        parameter.parsing.measurements.outliers_elimination,
                        parameter.parsing.measurements.upper_threshold_val)
            tfile.cutData(self.start_t, self.stop_t)

            if not frequencies:
                for s in tfile.session.series:
                    MDATA.add(s)
            else:
                for freq in frequencies:
                    MDATA.add(tfile.session.get_series(freq))

            if self.erase_txt:
                os.remove(tfile.path)
        return MDATA

    @staticmethod
    def update_calibr() -> None:
        ftp = ftplib.FTP(Settings.Server.IP)
        ftp.login(Settings.Server.login, Settings.Server.password)
        ftp.cwd(Settings.Server.calibrRoot)
        cflist = []
        try:
            cflist = ftp.nlst()
        except ftplib.all_errors:
            print('FTP error\t' + '[' + colored('Error', 'red') + ']')
            exit(550)
        cflist = [cfname for cfname in cflist if cfname.find(Settings.calibrPrefix) != -1]
        if os.path.exists(Settings.cfdataDir):
            for root, dirs, files in os.walk(Settings.cfdataDir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
                os.rmdir(Settings.cfdataDir)
            print('Removing calibration files\t' + '[' + colored('OK', 'green') + ']')
        os.makedirs(Settings.cfdataDir)
        for cfname in cflist:
            cfile_path = os.path.join(Settings.Server.calibrRoot, cfname)
            cfile_local_path = os.path.join(Settings.cfdataDir, cfname.encode(ftp.encoding).decode('utf8'))
            try:
                with open(cfile_local_path, 'wb') as cfile:
                    ftp.retrbinary('RETR ' + cfile_path, cfile.write)
            except ftplib.all_errors:
                print('FTP error\t' + cfname + '\t[' + colored('Error', 'red') + ']')
                if os.path.exists(cfile_local_path):
                    os.remove(cfile_local_path)
                exit(551)
        print('Calibration database update\t' + '[' + colored('OK', 'green') + ']')
