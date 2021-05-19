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
from datetime import datetime, date, time, timedelta
from borland_datetime import TDateTime
import wloader
from measurement import Measurement
from settings import Settings, parameter
from drawer import Drawer
from strucfun import structural_functions
from weather import Weather
from reporter import Reports
from qw import MoistureContent


def createArgParser():
    p = argparse.ArgumentParser()
    p.add_argument('--meteo', nargs='+',
                   default="['meteo_1_2017-01-01_2019-09-01.csv', 'meteo_2_2017-01-01_2019-09-01.csv']",
                   help="""Choose CSV-files of weather data.
                   Using: [--meteo filepath_1 filepath_2 ... filepath_N ].
                   Obtain meteodata: http://orash.ire.rssi.ru/meteo/index.php"""
                   )
    p.add_argument('--update_meteo', action='store_true', default='0',
                   help="""Update weather data with --meteo csv-files.
                   If --meteo is missing (by default), following files are used:
                   './meteo_1_2017-01-01_2019-09-01.csv', './meteo_2_2017-01-01_2019-09-01.csv'""")

    p.add_argument('--update_calibr', action='store_true', default=False,
                   help="Download files used for primary calibration of measurements.")

    # P22M_2017_08_01__05-09-34 - метка измерительного сеанса по умолчанию (год|месяц|день...)
    p.add_argument('-Y', '--year', default='2017', help='Year in YYYY format (2017 by default).')
    p.add_argument('-M', '--month', default='08', help='Month in MM format (08 by default).')
    p.add_argument('-D', '--day', default='01', help='Day in DD format (01 by default).')
    p.add_argument('-H', '--hh', default='05', help='Hour in hh format (05 by default).')
    p.add_argument('-m', '--mm', default='09', help='Minute in mm format (09 by default).')
    p.add_argument('-s', '--ss', default='34', help='Second in ss format (34 by default).')

    p.add_argument('--range', action='store_true', default=False,
                   help="""Set interval of measurements. 
                   If necessary, several consecutive measurement sessions are combined into one. 
                   For specifying the interval beginning, the values under keys 
                   -Y, -M, -D, -H, -m, -s are used. For specifying the end, please, use keys
                   --Y1, --M1, --D1, --H1, --m1, --s1 (listed below).""")

    p.add_argument('--sameday', action='store_true', default=False,
                   help='The keys --Y1, --M1, --D1 will be set equal to -Y, -M, -D.')

    p.add_argument('--Y1', default='2017', help='Year in YYYY format (2017 by default). ' +
                                                'Use with --range')
    p.add_argument('--M1', default='08', help='Month in MM format (08 by default). ' +
                                              'Use with --range')
    p.add_argument('--D1', default='01', help='Day in DD format (01 by default). ' +
                                              'Use with --range')
    p.add_argument('--H1', default='07', help='Hour in hh format(07 by default). ' +
                                              'Use with --range')
    p.add_argument('--m1', default='57', help='Minute in mm format (00 by default). ' +
                                              'Use with --range')
    p.add_argument('--s1', default='00', help='Second in ss format (00 by default). ' +
                                              'Use with --range')

    p.add_argument('--erase', action='store_true', default=False,
                   help="Add keys --eraserar, --erasedat and --erasetxt.")

    p.add_argument('--eraserar', action='store_true', default=False,
                   help="Delete RAR-files.")

    p.add_argument('--erasedat', action='store_true', default=False,
                   help="Delete DAT-files.")

    p.add_argument('--erasetxt', action='store_true', default=False,
                   help="Delete TXT-files.")

    p.add_argument('--nosf', action='store_true', default=False,
                   help="Do not calculate structural functions.")

    p.add_argument('--noweather', action='store_true', default=False,
                   help="Do not load weather data.")

    p.add_argument('--noqw', action='store_true', default=False,
                   help="No moisture content analysis.")

    p.add_argument('--closeplots', action='store_true', default=False,
                   help="Show and close plots immediately.")

    p.add_argument('--noplots', action='store_true', default=False,
                   help="Do not process plots.")

    p.add_argument('--saveplots', action='store_true', default=False,
                   help="Save plots to --plotroot directory.")

    p.add_argument('--plotroot', default=Settings.Plots.PlotRoot,
                   help="Where to store images? By default: " + Settings.Plots.PlotRoot)

    p.add_argument('--savereports', action='store_true', default=False,
                   help="Save all reports to --reportroot directory.")

    p.add_argument('--tbreport', action='store_true', default=False,
                   help="Save report on brightness temperatures.")

    p.add_argument('--sfreport', action='store_true', default=False,
                   help="Save report on structural functions.")

    p.add_argument('--wreport', action='store_true', default=False,
                   help="Save weather report.")

    p.add_argument('--qwreport', action='store_true', default=False,
                   help="Save report on moisture content parameters.")

    p.add_argument('--qwsfreport', action='store_true', default=False,
                   help="Save report on structural functions of moisture content parameters.")

    p.add_argument('--reportroot', default=Settings.Reports.ReportRoot,
                   help="Where to store reports? By default: " + Settings.Reports.ReportRoot)

    p.add_argument('--txtparsermode', default='',
                   help="Set TXT-parser special mode.")

    p.add_argument('--rangespec', default='',
                   help="Specify interval of measurements with string of \'YYYY-MM-DD : hh:mm - hh:mm\' format.")

    p.add_argument('--recycle', default='',
                   help="Specify how many times brightness temperature series are repeated.")

    return p


if __name__ == '__main__':
    parser = createArgParser()
    ns = parser.parse_args(sys.argv[1:])

    # Подготовка базы данных погоды
    if int(ns.update_meteo):
        wloader.delete()

    wloader.load(
        re.split(' ', re.sub(r"[\[\]',]", '', ns.meteo)),
        base=Settings.meteoBaseDir
    )

    # Подготовка базы калибровки
    if int(ns.update_calibr) or not(os.path.exists(Settings.cfdataDir)):
        Measurement.update_calibr()

    if ns.rangespec:
        ns.range, ns.sameday = True, True
        ns.year = ns.rangespec[0:4]
        ns.month = ns.rangespec[5:7]
        ns.day = ns.rangespec[8:10]
        ns.hh = ns.rangespec[13:15]
        ns.mm = ns.rangespec[16:18]
        ns.H1 = ns.rangespec[21:23]
        ns.m1 = ns.rangespec[24:26]

    start, stop = None, None
    try:
        d_start = date(int(ns.year), int(ns.month), int(ns.day))
        t_start = time(int(ns.hh), int(ns.mm), int(ns.ss))
        start = datetime.combine(d_start, t_start)
        stop = start + timedelta(hours=3)
        if int(ns.range):
            d_stop = date(int(ns.Y1), int(ns.M1), int(ns.D1))
            t_stop = time(int(ns.H1), int(ns.m1), int(ns.s1))
            if int(ns.sameday):
                d_stop = d_start
            stop = datetime.combine(d_stop, t_stop)
    except Exception as e:
        print('Wrong input. Exception occurred: \n{}'.format(e))
        exit(1989)

    if int(ns.erase):
        ns.eraserar, ns.erasedat, ns.erasetxt = True, True, True

    if int(ns.savereports):
        ns.tbreport, ns.sfreport, ns.wreport = True, True, True

    lbl = start.strftime(Settings.radiometerPrefix + '_%Y%m%d%H%M%S-') + stop.strftime('%Y%m%d%H%M%S')
    if int(ns.sameday):
        lbl = start.strftime('%Y%m%d-%H%M-') + stop.strftime('%H%M')

    m = Measurement(start=start, stop=stop,
                    erase_rar=ns.eraserar, erase_dat=ns.erasedat, erase_txt=ns.erasetxt,
                    tfparsemode=ns.txtparsermode)
    if ns.recycle:
        m.recycleData(int(ns.recycle))

    # Установка директорий для сохранения графиков и отчётности
    Settings.Plots.refresh(ns.plotroot)
    Settings.Reports.refresh(ns.reportroot)

    d = Drawer()

    savefig_path = None
    if int(ns.saveplots):  # Сохранять графики
        if not os.path.exists(Settings.Plots.PlotRoot):
            os.makedirs(Settings.Plots.PlotRoot)
        if not os.path.exists(Settings.Plots.TbPlotDir):
            os.makedirs(Settings.Plots.TbPlotDir)
        savefig_path = os.path.join(Settings.Plots.TbPlotDir, lbl + '.tb' + '.png')

    if not int(ns.noplots):
        d.draw(m.DATA,
               # title=u'Brightness temperatures',
               xlabel=u'время (чч:мм)', ylabel=u'Яркостная температура, K',
               labels=parameter.plot.labels('ru').basic_plus,
               colors=parameter.plot.colors.basic_plus,
               linestyles=parameter.plot.linestyles.basic_plus,
               linewidth=1.35, timeformat='hm',
               savefig_path=savefig_path)

    if int(ns.tbreport):
        if not os.path.exists(Settings.Reports.ReportRoot):
            os.makedirs(Settings.Reports.ReportRoot)
        if not os.path.exists(Settings.Reports.TbReportDir):
            os.makedirs(Settings.Reports.TbReportDir)
        report_path = os.path.join(Settings.Reports.TbReportDir, lbl + '.tb' + '.txt')
        Reports.makeTable(m.DATA, report_path)

    if not int(ns.nosf):
        SFData = structural_functions(m.DATA)

        savefig_path = None
        if int(ns.saveplots):  # Сохранять графики
            if not os.path.exists(Settings.Plots.SFPlotDir):
                os.makedirs(Settings.Plots.SFPlotDir)
            savefig_path = os.path.join(Settings.Plots.SFPlotDir, lbl + '.sf' + '.png')

        if not int(ns.noplots):
            d.draw(SFData,
                   # title=u'Structural functions',
                   xlabel=u'сек.',
                   ylabel=u'Кв. корень структурной ф-ции, K',
                   labels=parameter.plot.labels('ru').basic_plus,
                   colors=parameter.plot.colors.basic_plus,
                   marker=True, timeformat='!s',
                   savefig_path=savefig_path,
                   x_ticks_step=TDateTime(ss=33).toDouble(),
                   axvlines=[TDateTime(ss=33).toDouble(),
                             TDateTime(ss=66).toDouble(),
                             TDateTime(mm=1, ss=39).toDouble(),
                             # TDateTime(mm=2, ss=34).toDouble(),
                             # TDateTime(mm=3, ss=18).toDouble()
                             ])

        if int(ns.sfreport):
            if not os.path.exists(Settings.Reports.ReportRoot):
                os.makedirs(Settings.Reports.ReportRoot)
            if not os.path.exists(Settings.Reports.SFReportDir):
                os.makedirs(Settings.Reports.SFReportDir)
            report_path = os.path.join(Settings.Reports.SFReportDir, lbl + '.sf' + '.txt')
            Reports.makeTable(SFData, report_path,
                              apply_to_timestamp=lambda t: TDateTime.fromDouble(t).strSeconds())
            report_path_transposed = os.path.join(Settings.Reports.SFReportDir, lbl + '.sf_transposed' + '.txt')
            Reports.makeTableTransposed(SFData, report_path_transposed,
                                        apply_to_timestamp=lambda t: TDateTime.fromDouble(t).strSeconds())

    if not int(ns.noweather):
        w = Weather(start, stop)

        savefig_path = None
        if int(ns.saveplots):  # Сохранять графики
            if not os.path.exists(Settings.Plots.WeatherPlotDir):
                os.makedirs(Settings.Plots.WeatherPlotDir)
            savefig_path = os.path.join(Settings.Plots.WeatherPlotDir, lbl + '.weather' + '.png')

        if not int(ns.noplots):
            w.apply(formatstr='trw*')
            d.draw(w.DATA,
                   title=u'Weather', xlabel=u'hh:mm (time)', ylabel=u'Values',
                   labels=parameter.plot.labels('en').weather,
                   colors=parameter.plot.colors.weather,
                   linewidth=1.35, timeformat='hm',
                   savefig_path=savefig_path)

        w.apply()

        if int(ns.wreport):
            if not os.path.exists(Settings.Reports.ReportRoot):
                os.makedirs(Settings.Reports.ReportRoot)
            if not os.path.exists(Settings.Reports.WeatherReportDir):
                os.makedirs(Settings.Reports.WeatherReportDir)
            report_path = os.path.join(Settings.Reports.WeatherReportDir, lbl + '.weather' + '.txt')
            Reports.makeTable(w.DATA, report_path)

        if not int(ns.noqw):
            c = MoistureContent(measurement=m, weather=w)

            Q_op, W_op = c.optimize()
            # Q_df, W_df = c.DUALFREQCPP()

            Q_op_sf = structural_functions(Q_op)
            W_op_sf = structural_functions(W_op)

            savefig_path_q_op, savefig_path_w_op = None, None
            savefig_path_q_df, savefig_path_w_df = None, None
            if int(ns.saveplots):
                if not os.path.exists(Settings.Plots.QWPlotDir):
                    os.makedirs(Settings.Plots.QWPlotDir)
                savefig_path_q_op = os.path.join(Settings.Plots.QWPlotDir, lbl + '.q_op' + '.png')
                savefig_path_w_op = os.path.join(Settings.Plots.QWPlotDir, lbl + '.w_op' + '.png')
                savefig_path_q_df = os.path.join(Settings.Plots.QWPlotDir, lbl + '.q_df' + '.png')
                savefig_path_w_df = os.path.join(Settings.Plots.QWPlotDir, lbl + '.w_df' + '.png')

            if not int(ns.noplots):

                d.draw(Q_op,
                       title=u'', xlabel=u'время (чч:мм)',
                       ylabel=r'г/см$^2$',
                       labels={'q': 'Полная масса водяного пара'},
                       colors={'q': 'black'},
                       linewidth=1.35, timeformat='hm',
                       savefig_path=savefig_path_q_op)
                d.draw(W_op,
                       title=u'', xlabel=u'время (чч:мм)',
                       ylabel=r'кг/м$^2$',
                       labels={'w': 'Водозапас облаков'},
                       colors={'w': 'black'},
                       linewidth=1.35, timeformat='hm',
                       savefig_path=savefig_path_w_op)

                d.draw(Q_op_sf,
                       title=u'', xlabel=u'сек.',
                       ylabel=u'Кв. корень структурной ф-ции для Q',
                       labels={'q': 'Полная масса водяного пара'},
                       colors={'q': 'black'},
                       marker=True, timeformat='!s',
                       x_ticks_step=TDateTime(ss=33).toDouble(),
                       axvlines=[TDateTime(ss=33).toDouble(),
                                 TDateTime(ss=66).toDouble(),
                                 TDateTime(mm=1, ss=39).toDouble(),
                                 ])
                d.draw(W_op_sf,
                       title=u'', xlabel=u'сек.',
                       ylabel=u'Кв. корень структурной ф-ции для W',
                       labels={'w': 'Водозапас облаков'},
                       colors={'w': 'black'},
                       marker=True, timeformat='!s',
                       x_ticks_step=TDateTime(ss=33).toDouble(),
                       axvlines=[TDateTime(ss=33).toDouble(),
                                 TDateTime(ss=66).toDouble(),
                                 TDateTime(mm=1, ss=39).toDouble(),
                                 ])

            if int(ns.qwreport):
                if not os.path.exists(Settings.Reports.ReportRoot):
                    os.makedirs(Settings.Reports.ReportRoot)
                if not os.path.exists(Settings.Reports.QWReportDir):
                    os.makedirs(Settings.Reports.QWReportDir)
                report_path = os.path.join(Settings.Reports.QWReportDir, lbl + '.q' + '.txt')
                Reports.makeTable(Q_op, report_path, apply_to_timestamp=lambda t: TDateTime.fromDouble(t).strSeconds())
                report_path = os.path.join(Settings.Reports.QWReportDir, lbl + '.w' + '.txt')
                Reports.makeTable(W_op, report_path, apply_to_timestamp=lambda t: TDateTime.fromDouble(t).strSeconds())

            if int(ns.qwsfreport):
                if not os.path.exists(Settings.Reports.ReportRoot):
                    os.makedirs(Settings.Reports.ReportRoot)
                if not os.path.exists(Settings.Reports.QWReportDir):
                    os.makedirs(Settings.Reports.QWReportDir)
                report_path = os.path.join(Settings.Reports.QWReportDir, lbl + '.q_sf' + '.txt')
                Reports.makeTable(Q_op_sf, report_path, apply_to_timestamp=lambda t: TDateTime.fromDouble(t).strSeconds())
                report_path = os.path.join(Settings.Reports.QWReportDir, lbl + '.w_sf' + '.txt')
                Reports.makeTable(W_op_sf, report_path, apply_to_timestamp=lambda t: TDateTime.fromDouble(t).strSeconds())

    if not int(ns.closeplots):
        d.show()
