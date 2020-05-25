# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

import os

radiometerName = 'P22M'


class Settings:
    # Be careful! Do not set '/' path
    meteoBaseDir = './w/'
    radiometerPrefix = radiometerName
    bfdataDir = './bf/'
    tfdataDir = './tf/'
    cfdataDir = './cf/'
    calibrPrefix = 'calibr23'
    calibrPostfix = 'p22m'

    swvapour_conf_path = './saturated_wvpr.conf'

    class Plots:
        PlotRoot = './pic/'
        TbPlotDir = os.path.join(PlotRoot, 'tb/')
        WeatherPlotDir = os.path.join(PlotRoot, 'weather/')
        SFPlotDir = os.path.join(PlotRoot, 'sf/')
        QWPlotDir = os.path.join(PlotRoot, 'qw/')

        @staticmethod
        def refresh(_PlotRoot: str):
            Settings.Plots.PlotRoot = _PlotRoot
            Settings.Plots.TbPlotDir = os.path.join(Settings.Plots.PlotRoot, 'tb/')
            Settings.Plots.WeatherPlotDir = os.path.join(Settings.Plots.PlotRoot, 'weather/')
            Settings.Plots.SFPlotDir = os.path.join(Settings.Plots.PlotRoot, 'sf/')
            Settings.Plots.QWPlotDir = os.path.join(Settings.Plots.PlotRoot, 'qw/')

    class Reports:
        ReportRoot = './reports/'
        TbReportDir = os.path.join(ReportRoot, 'tb/')
        WeatherReportDir = os.path.join(ReportRoot, 'weather/')
        SFReportDir = os.path.join(ReportRoot, 'sf/')
        QWReportDir = os.path.join(ReportRoot, 'qw/')

        @staticmethod
        def refresh(_ReportRoot: str):
            Settings.Reports.ReportRoot = _ReportRoot
            Settings.Reports.TbReportDir = os.path.join(Settings.Reports.ReportRoot, 'tb/')
            Settings.Reports.WeatherReportDir = os.path.join(Settings.Reports.ReportRoot, 'weather/')
            Settings.Reports.SFReportDir = os.path.join(Settings.Reports.ReportRoot, 'sf/')
            Settings.Reports.QWReportDir = os.path.join(Settings.Reports.ReportRoot, 'qw/')

    class Server:
        IP = '217.107.96.189'
        login = 'ftprad'
        password = 'radireftp'

        measurementsRoot = os.path.join('/home/rad/', radiometerName)
        year_path = {2019: os.path.join(measurementsRoot, '2019/'),
                     2018: os.path.join(measurementsRoot, '2018/'),
                     2017: os.path.join(measurementsRoot, '2017/')}

        calibrRoot = os.path.join('/home/rad/', radiometerName, 'calibr/')

    class Markup:
        class Old:
            categories = {1: 'ncl', 2: 'cl1-', 3: 'cl2-', 4: 'cl1+', 5: 'cl2+', 6: 'mix', 7: 'badw'}

            summerCategories = {1: 'sncl', 2: 'sclm1', 3: 'sclm2', 4: 'sclp1', 5: 'sclp2', 6: 'smix', 7: 'sbadw'}
            winterCategories = {1: 'wncl', 2: 'wclm1', 3: 'wclm2', 4: 'wclp1', 5: 'wclp2', 6: 'wmix', 7: 'wbadw'}

        categories = {1: 'N cl', 2: 'Cu hum', 3: 'Cu med', 4: 'Cu cong', 5: 'Cb', 6: 'Cb+',
                      7: 'St', 8: 'St+', 9: 'Sc', 10: 'Ns', 11: 'Ns+'}

        summerCategories = {1: 'N cl', 2: 'Cu hum', 3: 'Cu med', 4: 'Cu cong', 5: 'Cb+', 6: 'Sc', 7: 'Ns+'}
        winterCategories = {1: 'N cl', 2: 'Cu med', 3: 'St', 4: 'St+', 5: 'Sc'}
