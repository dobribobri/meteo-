# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

import os
import sys
import argparse
import regex as re
import wloader
from settings import Settings
import ftplib
from termcolor import colored
import default
from strucfun import structural_functions
from drawer import Drawer
from weather import Weather
from qw import QW
from datetime import datetime
from measurement import Measurement
from reporter import Reporter
from dprinter import printDATA
import turbulence


def createArgParser():
    parser_ = argparse.ArgumentParser()
    parser_.add_argument('--meteo', nargs='+',
                         default="['meteo_1_2017-01-01_2019-09-01.csv', 'meteo_2_2017-01-01_2019-09-01.csv']",
                         help="Выбор файлов метеорологической базы данных (CSV). " +
                              "Использование: [--meteo путь_к_файлу_CSV_1 " +
                              "путь_к_файлу_CSV_2 ... путь_к_файлу_CSV_N ]. " +
                              "Метеоданные в формате CSV можно получить по адресу URL: " +
                              "http://orash.ire.rssi.ru/meteo/index.php")
    parser_.add_argument('--update_meteo', action='store_true', default='0',
                         help="Обновить метеорологическую базу данных. В процессе обновления будут использованы " +
                              "CSV файлы, указанные под флагом --meteo. " +
                              "Если флаг --meteo отсутствует (по умолчанию), то " +
                              "используются следующие файлы: './meteo_1_2017-01-01_2019-09-01.csv', "
                              "'./meteo_2_2017-01-01_2019-09-01.csv'")

    parser_.add_argument('--update_calibr', action='store_true', default='0',
                         help="Обновить базу файлов (первичной) калибровки (загрузка с сервера).")

    # P22M_2017_08_01__05-09-34 - метка измерительного сеанса по умолчанию (год|месяц|день...)
    parser_.add_argument('-Y', '--year', default='2017', help='Год в формате YYYY (2017 по умолчанию).')
    parser_.add_argument('-M', '--month', default='08', help='Месяц в формате MM (08 по умолчанию).')
    parser_.add_argument('-D', '--day', default='01', help='День в формате DD (01 по умолчанию).')
    parser_.add_argument('-H', '--hh', default='05', help='Час в формате hh (05 по умолчанию).')
    parser_.add_argument('-m', '--mm', default='09', help='Минута в формате mm (09 по умолчанию).')
    parser_.add_argument('-s', '--ss', default='34', help='Секунда в формате ss (34 по умолчанию).')

    parser_.add_argument('--range', action='store_true', default='0',
                         help="Задать временной интервал измерений. При необходимости, несколько последовательных " +
                              "измерительных сеансов будут объеденены в один. " +
                              "За дату и время начала диапазона (временного интервала) принимаются значения " +
                              "под ключами -Y, -M, -D, -H, -m, -s. " +
                              "Для указания даты и времени окончания диапазона используйте " +
                              "--Y1, --M1, --D1, --H1, --m1, --s1 (приведены ниже).")

    parser_.add_argument('--sameday', action='store_true', default='0',
                         help='Ключи --Y1, --M1, --D1 устанавливаются равными -Y, -M, -D.')

    parser_.add_argument('--Y1', default='2017', help='Год в формате YYYY (2017 по умолчанию). ' +
                                                      'Не используется без --range')
    parser_.add_argument('--M1', default='08', help='Месяц в формате MM (08 по умолчанию). ' +
                                                    'Не используется без --range')
    parser_.add_argument('--D1', default='01', help='День в формате DD (01 по умолчанию). ' +
                                                    'Не используется без --range')
    parser_.add_argument('--H1', default='07', help='Час в формате hh (07 по умолчанию). ' +
                                                    'Не используется без --range')
    parser_.add_argument('--m1', default='57', help='Минута в формате mm (57 по умолчанию). ' +
                                                    'Не используется без --range')
    parser_.add_argument('--s1', default='00', help='Секунда в формате ss (00 по умолчанию). ' +
                                                    'Не используется без --range')

    parser_.add_argument('--erase', action='store_true', default='0',
                         help="Удалить файлы данных измерительного сеанса по окончанию работы программы.")

    parser_.add_argument('--nosf', action='store_true', default='0',
                         help="Не вычислять значения структурных функций.")

    parser_.add_argument('--noweather', action='store_true', default='0',
                         help="Не подгружать данные погоды (--noqw будет устновлен автоматически).")

    parser_.add_argument('--noqw', action='store_true', default='0',
                         help="Не вычислять значения интегральных параметров влагосодержания атмосферы.")

    parser_.add_argument('--continuous', action='store_true', default='0',
                         help="Закрыть графики сразу же после отрисовки.")

    parser_.add_argument('--noplots', action='store_true', default='0',
                         help="Вообще не рисовать графики.")

    parser_.add_argument('--saveplots', action='store_true', default='0',
                         help="Сохранять отрисованные графики в директорию --plotroot")

    parser_.add_argument('--plotroot', default=Settings.Plots.PlotRoot,
                         help="Куда сохранять изображения? " +
                              "По умолчанию: " + Settings.Plots.PlotRoot)

    parser_.add_argument('--nocturb', action='store_true', default='0',
                         help="Не рисовать постоянную турбулентности.")

    # parser_.add_argument('--tbplotdir', default=Settings.Plots.TbPlotDir,
    #                      help="Куда сохранять графики временного хода яркостных температур? " +
    #                           "По умолчанию: " + Settings.Plots.TbPlotDir)
    #
    # parser_.add_argument('--sfplotdir', default=Settings.Plots.SFPlotDir,
    #                      help="Куда сохранять графики значений структурных функций? " +
    #                           "По умолчанию: " + Settings.Plots.SFPlotDir)
    #
    # parser_.add_argument('--weatherplotdir', default=Settings.Plots.WeatherPlotDir,
    #                      help="Куда сохранять графики погодных параметров? " +
    #                           "По умолчанию: " + Settings.Plots.WeatherPlotDir)
    #
    # parser_.add_argument('--qwplotdir', default=Settings.Plots.QWPlotDir,
    #                      help="Куда сохранять графики полной массы водяного пара и водозапаса облаков? " +
    #                           "По умолчанию: " + Settings.Plots.QWPlotDir)

    parser_.add_argument('--savereports', action='store_true', default='0',
                         help="Сохранять обобщённые данные графиков в текстовом виде (сохранять отчёты). " +
                              "Директория для сохранения: --reportroot")

    parser_.add_argument('--reportroot', default=Settings.Reports.ReportRoot,
                         help="Куда сохранять отчёты? " +
                              "По умолчанию: " + Settings.Reports.ReportRoot)

    # parser_.add_argument('--tbreportdir', default=Settings.Reports.TbReportDir,
    #                      help="Куда сохранить отчёт по яркостным температурам? " +
    #                           "По умолчанию: " + Settings.Reports.TbReportDir)
    #
    # parser_.add_argument('--sfreportdir', default=Settings.Reports.SFReportDir,
    #                      help="Куда сохранить отчёт по структурным функциям? " +
    #                           "По умолчанию: " + Settings.Reports.SFReportDir)
    #
    # parser_.add_argument('--weatherreportdir', default=Settings.Reports.WeatherReportDir,
    #                      help="Куда сохранить отчёт по погоде? " +
    #                           "По умолчанию: " + Settings.Reports.WeatherReportDir)
    #
    # parser_.add_argument('--qwreportdir', default=Settings.Reports.QWReportDir,
    #                      help="Куда сохранить отчёт по значениям интегральных параметров? " +
    #                           "По умолчанию: " + Settings.Reports.QWReportDir)

    parser_.add_argument('--txtparsermode', default='',
                         help="Режим парсера текстовых файлов.")

    parser_.add_argument('--noconnection', action='store_true', default='0',
                         help="Не подключаться к серверу.")

    return parser_


def delete_w_base_if_exists():
    if os.path.exists(Settings.meteoBaseDir):
        for root, dirs, files in os.walk(Settings.meteoBaseDir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(Settings.meteoBaseDir)
        print('Удаление базы метеорологических данных\t' + '[' + colored('OK', 'green') + ']')
    return


def update_calibr():
    ftp_ = ftplib.FTP(Settings.Server.IP)
    ftp_.login(Settings.Server.login, Settings.Server.password)
    ftp_.cwd(Settings.Server.calibrRoot)
    cflist = []
    try:
        cflist = ftp_.nlst()
    except:
        print('Ошибка FTP. Не удалось получить список файлов\t' + '[' + colored('Error', 'red') + ']')
        exit(550)

    ecflist = []
    for cfname in cflist:
        if cfname.find(Settings.calibrPrefix) != -1:
            ecflist.append(cfname)
    cflist = ecflist[:]
    ecflist.clear()

    if os.path.exists(Settings.cfdataDir):
        for root, dirs, files in os.walk(Settings.cfdataDir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
            os.rmdir(Settings.cfdataDir)
        print('Удаление базы файлов калибровки\t' + '[' + colored('OK', 'green') + ']')
    os.makedirs(Settings.cfdataDir)

    for cfname in cflist:
        cfile_path = os.path.join(Settings.Server.calibrRoot, cfname)
        cfile_local_path = os.path.join(Settings.cfdataDir, cfname.encode(ftp_.encoding).decode('utf8'))
        try:
            with open(cfile_local_path, 'wb') as cfile:
                ftp_.retrbinary('RETR ' + cfile_path, cfile.write)
        except:
            print('Ошибка FTP. Не удалось загрузить файл\t' + cfname + '\t[' + colored('Error', 'red') + ']')
            if os.path.exists(cfile_local_path):
                os.remove(cfile_local_path)
            exit(551)
    print('Обновление базы файлов калибровки\t' + '[' + colored('OK', 'green') + ']')
    return


if __name__ == '__main__':
    parser = createArgParser()
    namespace = parser.parse_args(sys.argv[1:])

    # Подготовка базы данных погоды
    if int(namespace.update_meteo):
        delete_w_base_if_exists()

    wloader.load(
        re.split(' ', re.sub("[\[\]',]", '', namespace.meteo)),
        base=Settings.meteoBaseDir
    )

    # Подготовка базы калибровки
    if int(namespace.update_calibr):
        update_calibr()

    # Подготовка измерительных сеансов - работа с введёнными датами
    DateTime_start = datetime(2017, 8, 1, 5, 9, 34)
    DateTime_stop = None
    try:
        DateTime_start = datetime(int(namespace.year), int(namespace.month), int(namespace.day),
                                  int(namespace.hh), int(namespace.mm), int(namespace.ss))
        if int(namespace.range):
            if int(namespace.sameday):
                namespace.Y1 = namespace.year
                namespace.M1 = namespace.month
                namespace.D1 = namespace.day
            DateTime_stop = datetime(int(namespace.Y1), int(namespace.M1), int(namespace.D1),
                                     int(namespace.H1), int(namespace.m1), int(namespace.s1))
    except Exception as e:
        print('Неверный ввод. Возникло исключение: \n{}'.format(e))
        exit(1989)

    # Установка директорий для сохранения графиков и отчётности
    Settings.Plots.refresh(namespace.plotroot)
    Settings.Reports.refresh(namespace.reportroot)

    ################################################################

    # Выбран единичный сеанс
    if not int(namespace.range):
        # Получение яркостных температур
        print(namespace.txtparsermode)
        m = Measurement(DateTime_start, erase=namespace.erase,
                        tfparsemode=namespace.txtparsermode,
                        noconnection=int(namespace.noconnection))
        DATA = m.getDATA()

        mlbl = m.construct_mlbl_(DateTime_start)

        # printDATA(m.DATA, shortened=True)
        drawer = Drawer()  # Используется для отрисовки графиков
        reporter = Reporter(global_report_path=os.path.join(Settings.Reports.ReportRoot, 'global.txt'))
        # Используется для составления отчётов

        if not int(namespace.noplots):
            # Отрисовка графиков яркостных температур
            savefig_path = ''
            if int(namespace.saveplots):  # Сохранять графики
                if not os.path.exists(Settings.Plots.PlotRoot):
                    os.makedirs(Settings.Plots.PlotRoot)
                if not os.path.exists(Settings.Plots.TbPlotDir):
                    os.makedirs(Settings.Plots.TbPlotDir)
                savefig_path = os.path.join(Settings.Plots.TbPlotDir, mlbl + '.tb' + '.png')
            drawer.drawDATA(DATA, title=u'', xlabel=u'time (hh:mm)', ylabel=u'Brightness temperature, K',
                            labels=default.parameter.plot.labels('en').basic_plus,
                            colors=default.parameter.plot.colors.basic_plus,
                            linestyles=default.parameter.plot.linestyles.basic_plus,
                            linewidth=1.35, timeformat='hm',
                            savefig_path=savefig_path)
        if int(namespace.savereports):
            if not os.path.exists(Settings.Reports.ReportRoot):
                os.makedirs(Settings.Reports.ReportRoot)
            if not os.path.exists(Settings.Reports.TbReportDir):
                os.makedirs(Settings.Reports.TbReportDir)
            report_path = os.path.join(Settings.Reports.TbReportDir, mlbl + '.tb' + '.txt')
            reporter.set(DATA, report_path, mlbl)
            reporter.makeTbReport()

        if not int(namespace.nosf):
            # Получение значений структурных функций
            SFDATA = structural_functions(m,
                                          default.parameter.struct_func.thinning,
                                          default.parameter.struct_func.part)
            # printDATA(SFDATA, shortened=True)

            # C_alpha = turbulence.c_alpha(SFDATA)
            # drawer.drawDATA(C_alpha, title=r'$C_{\alpha}$',
            #                 xlabel=u'sec.',
            #                 ylabel=r'$10^{-3}\cdot$K$^{-1}\cdot$m$^{-\frac{8}{3}}$',
            #                 labels=default.parameter.plot.labels('en').basic_plus,
            #                 colors=default.parameter.plot.colors.basic_plus,
            #                 timeformat='ms'
            #                 )

            # maxlen = 0
            # s = 'time '
            # for freq in SFDATA.keys():
            #     s += str(freq) + ' '
            #     if len(SFDATA[freq]) > maxlen:
            #         maxlen = len(SFDATA[freq])
            # with open('./analysis/bb.txt', 'w') as a02f:
            #     a02f.write(s[:-1] + '\n')
            #     for i in range(1, maxlen):
            #         s = str(i*11) + ' '
            #         for freq in SFDATA.keys():
            #             try:
            #                 _, val = SFDATA[freq][i]
            #                 s += str(val) + ' '
            #             except IndexError:
            #                 s += '0 '
            #         a02f.write(s[:-1] + '\n')

            if not int(namespace.noplots):
                # Отрисовка значений структурных функций
                savefig_path = ''
                if int(namespace.saveplots):  # Сохранять графики
                    if not os.path.exists(Settings.Plots.SFPlotDir):
                        os.makedirs(Settings.Plots.SFPlotDir)
                    savefig_path = os.path.join(Settings.Plots.SFPlotDir, mlbl + '.sf' + '.png')
                drawer.drawDATA(SFDATA, title=u'Structural functions', xlabel=u'mm:ss (time)', ylabel='sqrt(S)',
                                labels=default.parameter.plot.labels('en').basic_plus,
                                colors=default.parameter.plot.colors.basic_plus,
                                marker=True, timeformat='ms',
                                savefig_path=savefig_path,
                                axvlines=[default.parameter.struct_func.borland.t_sec(25),
                                          default.parameter.struct_func.borland.t_sec(50),
                                          default.parameter.struct_func.borland.t_sec(100),
                                          default.parameter.struct_func.borland.t_sec(150),
                                          default.parameter.struct_func.borland.t_sec(200)])
            if int(namespace.savereports):
                if not os.path.exists(Settings.Reports.SFReportDir):
                    os.makedirs(Settings.Reports.SFReportDir)
                report_path = os.path.join(Settings.Reports.SFReportDir, mlbl + '.sf' + '.txt')
                reporter.set(SFDATA, report_path, mlbl)
                reporter.makeSFReport()

        weather = None
        if not int(namespace.noweather):
            # Получение данных о погоде
            weather = Weather(*m.getTimeBounds())
            WeatherDATA = weather.getWeatherDATA(formatstr='trw*')
            WeatherDATA4report = weather.getWeatherDATA(formatstr='tmrhw*')

            if not int(namespace.noplots):
                # Отрисовка данных погоды
                savefig_path = ''
                if int(namespace.saveplots):  # Сохранять графики
                    if not os.path.exists(Settings.Plots.WeatherPlotDir):
                        os.makedirs(Settings.Plots.WeatherPlotDir)
                        savefig_path = os.path.join(Settings.Plots.WeatherPlotDir, mlbl + '.weather' + '.png')
                drawer.drawDATA(WeatherDATA, title=u'Weather', xlabel=u'hh:mm (time)', ylabel=u'Values',
                                labels=default.parameter.plot.labels('en').weather,
                                colors=default.parameter.plot.colors.weather,
                                linewidth=1.35, timeformat='hm',
                                savefig_path=savefig_path)
            if int(namespace.savereports):
                if not os.path.exists(Settings.Reports.WeatherReportDir):
                    os.makedirs(Settings.Reports.WeatherReportDir)
                report_path = os.path.join(Settings.Reports.WeatherReportDir, mlbl + '.weather' + '.txt')
                reporter.set(WeatherDATA4report, report_path, mlbl)
                reporter.makeWeatherReport()
        else:
            namespace.noqw = '1'

        if not int(namespace.noqw):
            # Получение полной массы водяного пара и водозапаса облаков
            QDATA, WDATA = QW(m, weather, Tavg=5, Tcl=-2).getQWDATA(freq_pairs=default.parameter.freqs.qw2_freq_pairs,
                                                                    time_step_sec=60,
                                                                    _w_correction=False)

            if not int(namespace.noplots):
                # Отрисовка значений интегральных параметров
                savefig_path_q, savefig_path_w = '', ''
                if int(namespace.saveplots):  # Сохранять графики
                    if not os.path.exists(Settings.Plots.QWPlotDir):
                        os.makedirs(Settings.Plots.QWPlotDir)
                    savefig_path_q = os.path.join(Settings.Plots.QWPlotDir, mlbl + '.q' + '.png')
                    savefig_path_w = os.path.join(Settings.Plots.QWPlotDir, mlbl + '.w' + '.png')
                drawer.drawDATA(QDATA, title=u'Total mass of water vapor', xlabel=u'hh:mm (time)',
                                ylabel=r'g/cm$^2$',
                                labels=default.parameter.plot.labels('en').qw2,
                                colors=default.parameter.plot.colors.qw2,
                                linewidth=1.35, timeformat='hm',
                                savefig_path=savefig_path_q)
                drawer.drawDATA(WDATA, title=u'Liquid water content in clouds', xlabel=u'hh:mm (time)',
                                ylabel=r'kg/m$^2$',
                                labels=default.parameter.plot.labels('en').qw2,
                                colors=default.parameter.plot.colors.qw2,
                                linewidth=1.35, timeformat='hm',
                                savefig_path=savefig_path_w)

        if not int(namespace.noplots):
            if not int(namespace.continuous):
                drawer.show()  # Показать графики и приостановить выполнение программы
            else:
                drawer.pause(1)  # Отрисовать и сразу же скрыть графики

        reporter.writeGlobal()

    ################################################################

    # Выбран диапазон измерительных сеансов
    else:
        # Получение яркостных температур
        m = Measurement(DateTime_start, DateTime_stop, erase=namespace.erase,
                        tfparsemode=namespace.txtparsermode,
                        noconnection=int(namespace.noconnection))
        DATA = m.getDATA()
        lbl = DateTime_start.strftime(Settings.radiometerPrefix + '_%Y%m%d%H%M%S-') + \
              DateTime_stop.strftime('%Y%m%d%H%M%S')
        if int(namespace.sameday):
            lbl = DateTime_start.strftime('%Y%m%d-%H%M-') + DateTime_stop.strftime('%H%M')

        drawer = Drawer()  # Используется для отрисовки графиков
        reporter = Reporter(global_report_path=os.path.join(Settings.Reports.ReportRoot, 'global.txt'))
        # Используется для составления отчётов

        if not int(namespace.noplots):
            # Отрисовать графики яркостных температур
            savefig_path = ''
            if int(namespace.saveplots):  # Сохранять графики
                if not os.path.exists(Settings.Plots.PlotRoot):
                    os.makedirs(Settings.Plots.PlotRoot)
                if not os.path.exists(Settings.Plots.TbPlotDir):
                    os.makedirs(Settings.Plots.TbPlotDir)
                savefig_path = os.path.join(Settings.Plots.TbPlotDir, lbl + '.tb' + '.png')
            drawer.drawDATA(DATA,
                            title=u'Brightness temperatures',
                            xlabel=u'time (hh:mm)', ylabel=u'Brightness temperature, K',
                            labels=default.parameter.plot.labels('en').basic_plus,
                            colors=default.parameter.plot.colors.basic_plus,
                            linestyles=default.parameter.plot.linestyles.basic_plus,
                            linewidth=1.35, timeformat='hm',
                            savefig_path=savefig_path)
        if int(namespace.savereports):
            if not os.path.exists(Settings.Reports.ReportRoot):
                os.makedirs(Settings.Reports.ReportRoot)
            if not os.path.exists(Settings.Reports.TbReportDir):
                os.makedirs(Settings.Reports.TbReportDir)
            report_path = os.path.join(Settings.Reports.TbReportDir, lbl + '.tb' + '.txt')
            reporter.set(DATA, report_path, lbl)
            reporter.makeTbReport()

        SFDATA = []
        if not int(namespace.nosf):
            # Получение значений структурных функций
            SFDATA = structural_functions(m,
                                          default.parameter.struct_func.thinning,
                                          default.parameter.struct_func.part)

            # printDATA(SFDATA, shortened=True)

            if not int(namespace.noplots):
                # Отрисовать графики структурных функций
                savefig_path = ''
                if int(namespace.saveplots):  # Сохранять графики
                    if not os.path.exists(Settings.Plots.SFPlotDir):
                        os.makedirs(Settings.Plots.SFPlotDir)
                    savefig_path = os.path.join(Settings.Plots.SFPlotDir, lbl + '.sf' + '.png')
                drawer.drawDATA(SFDATA, title=u'Structural functions', xlabel=u'sec.',
                                ylabel=u'sqrt(S), K',
                                labels=default.parameter.plot.labels('en').basic_plus,
                                colors=default.parameter.plot.colors.basic_plus,
                                marker=True, timeformat='!s',
                                savefig_path=savefig_path,
                                axvlines=[default.parameter.struct_func.borland.t_sec(25),
                                          default.parameter.struct_func.borland.t_sec(50),
                                          default.parameter.struct_func.borland.t_sec(100),
                                          default.parameter.struct_func.borland.t_sec(150),
                                          default.parameter.struct_func.borland.t_sec(200)])
            if int(namespace.savereports):
                if not os.path.exists(Settings.Reports.SFReportDir):
                    os.makedirs(Settings.Reports.SFReportDir)
                report_path = os.path.join(Settings.Reports.SFReportDir, lbl + '.sf' + '.txt')
                reporter.set(SFDATA, report_path, lbl)
                reporter.makeSFReport()
                report_path = os.path.join(Settings.Reports.SFReportDir, lbl + '.sf.full' + '.txt')
                reporter.set(SFDATA, report_path, lbl)
                reporter.makeFullSFReport()

        weather = None
        WeatherDATA = []
        if not int(namespace.noweather):
            # Получение данных о погоде
            weather = Weather(*m.getTimeBounds())
            WeatherDATA = weather.getWeatherDATA(formatstr='trw*')
            WeatherDATA4report = weather.getWeatherDATA(formatstr='tmrhw*')

            if not int(namespace.noplots):
                # Отрисовать графики погодных данных
                savefig_path = ''
                if int(namespace.saveplots):  # Сохранять графики
                    if not os.path.exists(Settings.Plots.WeatherPlotDir):
                        os.makedirs(Settings.Plots.WeatherPlotDir)
                    savefig_path = os.path.join(Settings.Plots.WeatherPlotDir, lbl + '.weather' + '.png')
                drawer.drawDATA(WeatherDATA, title=u'Weather', xlabel=u'hh:mm (time)', ylabel=u'Values',
                                labels=default.parameter.plot.labels('en').weather,
                                colors=default.parameter.plot.colors.weather,
                                linewidth=1.35, timeformat='hm',
                                savefig_path=savefig_path)
            if int(namespace.savereports):
                if not os.path.exists(Settings.Reports.WeatherReportDir):
                    os.makedirs(Settings.Reports.WeatherReportDir)
                report_path = os.path.join(Settings.Reports.WeatherReportDir, lbl + '.weather' + '.txt')
                reporter.set(WeatherDATA4report, report_path, lbl)
                reporter.makeWeatherReport()
        else:
            namespace.noqw = '1'

        if not int(namespace.nocturb):
            C_alpha = turbulence.c_alpha(SFDATA, WeatherDATA4report)
            drawer.drawDATA(C_alpha, title=r'$C_{\alpha}$',
                            xlabel=u'sec.',
                            ylabel=r'Value',
                            labels=default.parameter.plot.labels.basic_plus,
                            colors=default.parameter.plot.colors.basic_plus,
                            timeformat='!s', marker=True
                            )
            C_alpha = turbulence.c_alpha(SFDATA, WeatherDATA4report, colm_ob_lim=False)
            drawer.drawDATA(C_alpha, title=r'$C_{\alpha}$',
                            xlabel=u'sec.',
                            ylabel=r'Value',
                            labels=default.parameter.plot.labels.basic_plus,
                            colors=default.parameter.plot.colors.basic_plus,
                            timeformat='!s'
                            )

        if not int(namespace.noqw):
            QDATA, WDATA, MIN = QW(m, weather, Tavg=5, Tcl=-2).get_integrals_multifreq(time_step_sec=60)
            # Получение значений полной массы водяного пара и водозапаса облаков
            # QDATA, WDATA = QW(m, weather, Tavg=5, Tcl=-2).getQWDATA(freq_pairs=default.parameter.freqs.QW2_FREQ_PAIRS,
            #                                                         time_step_sec=60,
            #                                                         _w_correction=True)
            if not int(namespace.noplots):
                # Отрисовка значений интегральных параметров
                savefig_path_q, savefig_path_w = '', ''
                if int(namespace.saveplots):  # Сохранять графики
                    if not os.path.exists(Settings.Plots.QWPlotDir):
                        os.makedirs(Settings.Plots.QWPlotDir)
                    savefig_path_q = os.path.join(Settings.Plots.QWPlotDir, lbl + '.q' + '.png')
                    savefig_path_w = os.path.join(Settings.Plots.QWPlotDir, lbl + '.w' + '.png')
                # drawer.drawDATA(QDATA, title=u'Total mass of water vapor', xlabel=u'hh:mm (time)',
                #                                 ylabel=r'g/cm$^2$',
                #                                 labels=default.parameter.plot.labels('en').qw2,
                #                                 colors=default.parameter.plot.colors.qw2,
                #                                 linewidth=1.35, timeformat='hm',
                #                                 savefig_path=savefig_path_q)
                # drawer.drawDATA(WDATA, title=u'Liquid water content in clouds', xlabel=u'hh:mm (time)',
                #                                 ylabel=r'kg/m$^2$',
                #                                 labels=default.parameter.plot.labels('en').qw2,
                #                                 colors=default.parameter.plot.colors.qw2,
                #                                 linewidth=1.35, timeformat='hm',
                #                                 savefig_path=savefig_path_w)
                drawer.drawDATA(QDATA, title=u'Total mass of water vapor', xlabel=u'hh:mm (time)',
                                ylabel=r'g/cm$^2$',
                                labels={'multifreq': 'Multifreq'},
                                colors={'multifreq': 'darkblue'},
                                linewidth=1.35, timeformat='hm',
                                savefig_path=savefig_path_q)
                drawer.drawDATA(WDATA, title=u'Liquid water content in clouds', xlabel=u'hh:mm (time)',
                                ylabel=r'kg/m$^2$',
                                labels={'multifreq': 'Multifreq'},
                                colors={'multifreq': 'crimson'},
                                linewidth=1.35, timeformat='hm',
                                savefig_path=savefig_path_w)
                drawer.drawDATA(MIN, title=u'Несходимость', xlabel=u'hh:mm (время)',
                                ylabel=r'Значение',
                                labels={'multifreq': 'Multifreq'},
                                colors={'multifreq': 'crimson'},
                                linewidth=1.35, timeformat='hm',
                                savefig_path=savefig_path_w)

            if int(namespace.savereports):
                if not os.path.exists(Settings.Reports.QWReportDir):
                    os.makedirs(Settings.Reports.QWReportDir)
                report_path = os.path.join(Settings.Reports.QWReportDir, lbl + '.qw' + '.txt')
                reporter.path = report_path
                reporter.makeQWReport(QDATA, WDATA)

        if not int(namespace.noplots):
            if not int(namespace.continuous):
                drawer.show()  # Показать графики и приостановить выполнение программы
            else:
                drawer.pause(1)  # Отрисовать и сразу же скрыть графики

        reporter.writeGlobal()
