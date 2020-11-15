# -*- coding: utf-8 -*-
#
# # Dobroslav P. Egorov
# # Kotel'nikov Institute of Radio-engineering and Electronics of RAS
# # 2019
#

from session import *


class Reports:
    @staticmethod
    def makeTable(session: Session,
                  f_path: str, append: bool = False,
                  apply_to_timestamp=lambda t: t) -> None:
        print('Making report...')
        session.box()
        timestamps = session.get_timestamps_averaged()
        mode = 'w'
        if append:
            mode = 'a'
        with open(f_path, mode) as file:
            s = "time "
            for key in session.keys:
                s += str(key) + " "
            file.write(s + '\n')
            for t in timestamps:
                s = str(apply_to_timestamp(t)) + " "
                for series in session.series:
                    s += '{:.3f}'.format(series.get(t).val) + " "
                file.write(s + '\n')
