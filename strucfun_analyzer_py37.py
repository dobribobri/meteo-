# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

import regex as re
from collections import defaultdict
from settings import Settings
import os


class _Interval_:
    def __init__(self, Y: str, M: str, D: str, h_start: str, m_start: str,
                 h_stop: str, m_stop: str):
        self.Y, self.M, self.D, self.h_start, self.m_start, self.h_stop, self.m_stop = \
            Y, M, D, h_start, m_start, h_stop, m_stop


data = defaultdict(list)

with open('new_categories_2.txt', 'r') as markup:
    for line in markup:
        line = re.sub('[\r\n]', '', line)
        f = line.find('.')
        if f != -1:
            d = re.split(r'\.', line)
            category = d[0]
            print('\n' + category)
            continue
        if line == '':
            continue
        item = re.findall(r'\d{4}-\d{2}-\d{2} : \d{2}:\d{2} - \d{2}:\d{2}', line)
        if not item:
            print('-')
            continue
        item = item[0]
        ymd_times = re.split(' : ', item)
        ymd = re.split('-', ymd_times[0])
        times = re.split(' - ', ymd_times[1])
        hhmm0 = re.split(':', times[0])
        hhmm1 = re.split(':', times[1])
        print('{}-{}-{} : {}:{} - {}:{}'.format(ymd[0], ymd[1], ymd[2], hhmm0[0], hhmm0[1], hhmm1[0], hhmm1[1]))
        interval = _Interval_(ymd[0], ymd[1], ymd[2], hhmm0[0], hhmm0[1], hhmm1[0], hhmm1[1])
        data[category].append(interval)

# print(data)

for category in data.keys():
    # season = category[0]
    for i in data[category]:
        os.system('python3.7 main.py --year {} --month {} --day {}'.format(i.Y, i.M, i.D) +
                  ' --hh {} --mm {} --ss {}'.format(i.h_start, i.m_start, 0) +
                  ' --range --sameday --H1 {} --m1 {} --s1 {}'.format(i.h_stop, i.m_stop, 0) +
                  ' --saveplots --plotroot \'./analysis/{}/pics/\''.format(category) +
                  ' --savereports --reportroot \'./analysis/{}/reports/\''.format(category) +
                  ' --noqw --erase --continuous')

        print('python3.7 main.py --year {} --month {} --day {}'.format(i.Y, i.M, i.D) +
              ' --hh {} --mm {} --ss {}'.format(i.h_start, i.m_start, 0) +
              ' --range --sameday --H1 {} --m1 {} --s1 {}'.format(i.h_stop, i.m_stop, 0) +
              ' --saveplots --plotroot \'./analysis/{}/pics/\''.format(category) +
              ' --savereports --reportroot \'./analysis/{}/reports/\''.format(category) +
              ' --noqw --erase --continuous')

        # print('python3.7 main.py --year {} --month {} --day {}'.format(i.Y, i.M, i.D) +
        #       ' --hh {} --mm {} --ss {}'.format(i.h_start, i.m_start, 0) +
        #       ' --range --sameday --H1 {} --m1 {} --s1 {}'.format(i.h_stop, i.m_stop, 0) +
        #       ' --nosf --noweather --nocturb' +
        #       ' --noqw --continuous')
        #
        # os.system('python3.7 main.py --year {} --month {} --day {}'.format(i.Y, i.M, i.D) +
        #           ' --hh {} --mm {} --ss {}'.format(i.h_start, i.m_start, 0) +
        #           ' --range --sameday --H1 {} --m1 {} --s1 {}'.format(i.h_stop, i.m_stop, 0) +
        #           ' --nosf --noweather --nocturb' +
        #           ' --noqw --continuous')
